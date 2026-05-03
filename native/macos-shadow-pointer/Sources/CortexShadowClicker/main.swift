import CortexShadowPointerNative
import Foundation

#if canImport(AppKit)
import AppKit
#endif

struct ShadowClickerArgs {
    var smoke = false
    var json = false
    var duration: TimeInterval = 15

    init(_ arguments: [String]) throws {
        var iterator = arguments.dropFirst().makeIterator()
        while let argument = iterator.next() {
            switch argument {
            case "--smoke":
                smoke = true
            case "--json":
                json = true
            case "--duration":
                guard let value = iterator.next(), let parsed = TimeInterval(value), parsed > 0 else {
                    throw ShadowPointerNativeError.invalidControl("--duration requires a positive number")
                }
                duration = min(parsed, 300)
            default:
                throw ShadowPointerNativeError.invalidControl("unknown argument \(argument)")
            }
        }
    }
}

let encoder = JSONEncoder()
encoder.dateEncodingStrategy = .iso8601
encoder.keyEncodingStrategy = .convertToSnakeCase
encoder.outputFormatting = [.prettyPrinted, .sortedKeys]

do {
    let args = try ShadowClickerArgs(CommandLine.arguments)
    if args.smoke {
        let result = try NativeCursorFollowSmokeResult.run()
        if args.json {
            print(String(decoding: try encoder.encode(result), as: UTF8.self))
        } else {
            print("\(nativeCursorFollowBenchmarkID): passed=\(result.passed)")
        }
        if !result.passed {
            exit(1)
        }
        exit(0)
    }

    #if canImport(AppKit)
    if #available(macOS 13.0, *) {
        try MainActor.assumeIsolated {
            try ShadowClickerApp.run(duration: args.duration, encoder: encoder, emitJSON: args.json)
        }
    } else {
        throw ShadowPointerNativeError.invalidControl("cortex-shadow-clicker requires macOS 13+")
    }
    #else
    throw ShadowPointerNativeError.invalidControl("AppKit is required for cortex-shadow-clicker")
    #endif
} catch {
    fputs("Cortex Shadow Clicker failed: \(error)\n", stderr)
    exit(1)
}

#if canImport(AppKit)
@available(macOS 13.0, *)
@MainActor
final class ShadowClickerView: NSView {
    private let title = "Cortex"
    private let diameter: CGFloat

    init(diameter: CGFloat) {
        self.diameter = diameter
        super.init(frame: NSRect(x: 0, y: 0, width: diameter + 104, height: diameter + 30))
        wantsLayer = true
    }

    required init?(coder: NSCoder) {
        nil
    }

    override func draw(_ dirtyRect: NSRect) {
        NSColor.clear.setFill()
        dirtyRect.fill()

        let ringRect = NSRect(x: -1, y: diameter + 4, width: 24, height: 24)
        let ring = NSBezierPath(ovalIn: ringRect)
        NSColor(calibratedRed: 0.10, green: 0.38, blue: 0.82, alpha: 0.48).setStroke()
        ring.lineWidth = 2
        ring.stroke()
        NSColor(calibratedRed: 0.10, green: 0.38, blue: 0.82, alpha: 0.10).setFill()
        ring.fill()

        let cursor = NSBezierPath()
        cursor.move(to: NSPoint(x: 7, y: diameter + 24))
        cursor.line(to: NSPoint(x: 7, y: 6))
        cursor.line(to: NSPoint(x: 22, y: 18))
        cursor.line(to: NSPoint(x: 28, y: 5))
        cursor.line(to: NSPoint(x: 35, y: 8))
        cursor.line(to: NSPoint(x: 29, y: 21))
        cursor.line(to: NSPoint(x: 43, y: 23))
        cursor.close()

        let shadow = NSShadow()
        shadow.shadowBlurRadius = 12
        shadow.shadowOffset = NSSize(width: 0, height: -7)
        shadow.shadowColor = NSColor(calibratedWhite: 0.05, alpha: 0.28)
        NSGraphicsContext.saveGraphicsState()
        shadow.set()
        NSColor.white.setFill()
        cursor.fill()
        NSGraphicsContext.restoreGraphicsState()

        NSColor(calibratedRed: 0.10, green: 0.38, blue: 0.82, alpha: 1.0).setStroke()
        cursor.lineWidth = 2.4
        cursor.lineJoinStyle = .round
        cursor.stroke()

        let accent = NSBezierPath()
        accent.move(to: NSPoint(x: 22.2, y: 16.2))
        accent.line(to: NSPoint(x: 26.4, y: 7.2))
        accent.line(to: NSPoint(x: 28.8, y: 8.0))
        accent.line(to: NSPoint(x: 24.5, y: 17.1))
        accent.close()
        NSColor(calibratedRed: 0.08, green: 0.62, blue: 0.29, alpha: 0.96).setFill()
        accent.fill()

        let chipRect = NSRect(x: 42, y: 18, width: 54, height: 22)
        let chip = NSBezierPath(roundedRect: chipRect, xRadius: 11, yRadius: 11)
        NSColor(calibratedWhite: 1.0, alpha: 0.94).setFill()
        chip.fill()
        NSColor(calibratedWhite: 0.08, alpha: 0.14).setStroke()
        chip.lineWidth = 1
        chip.stroke()

        let attrs: [NSAttributedString.Key: Any] = [
            .font: NSFont.systemFont(ofSize: 11, weight: .semibold),
            .foregroundColor: NSColor(calibratedWhite: 0.10, alpha: 0.84),
        ]
        title.draw(at: NSPoint(x: 51, y: 22), withAttributes: attrs)
    }
}

@available(macOS 13.0, *)
@MainActor
final class ShadowClickerController {
    private let app: NSApplication
    private let panel: ShadowPointerOverlayPanel
    private let config: NativeCursorFollowConfig
    private let encoder: JSONEncoder
    private let emitJSON: Bool
    private var samples: [NativeCursorSample] = []
    private var followTimer: Timer?
    private var stopTimer: Timer?

    init(
        app: NSApplication,
        panel: ShadowPointerOverlayPanel,
        config: NativeCursorFollowConfig,
        encoder: JSONEncoder,
        emitJSON: Bool
    ) {
        self.app = app
        self.panel = panel
        self.config = config
        self.encoder = encoder
        self.emitJSON = emitJSON
    }

    func start(duration: TimeInterval) {
        let interval = 1.0 / Double(config.sampleHz)
        followTimer = Timer.scheduledTimer(withTimeInterval: interval, repeats: true) { [weak self] _ in
            Task { @MainActor in
                self?.tick()
            }
        }

        stopTimer = Timer.scheduledTimer(withTimeInterval: duration, repeats: false) { [weak self] _ in
            Task { @MainActor in
                self?.finish()
            }
        }
    }

    private func tick() {
        let sample = NativeCursorProbe.sampleNow()
        samples.append(sample)
        let nextOrigin = NSPoint(
            x: sample.x + config.offsetX,
            y: sample.y + config.offsetY
        )
        panel.setFrameOrigin(nextOrigin)
        panel.contentView?.needsDisplay = true
    }

    private func finish() {
        followTimer?.invalidate()
        stopTimer?.invalidate()
        let smokeSamples = samples.isEmpty ? [NativeCursorProbe.sampleNow()] : Array(samples.suffix(5))
        let result = try? NativeCursorFollowSmokeResult.run(samples: smokeSamples)
        panel.orderOut(nil)
        if emitJSON, let result, let data = try? encoder.encode(result) {
            print(String(decoding: data, as: UTF8.self))
        }
        app.terminate(nil)
    }
}

@available(macOS 13.0, *)
@MainActor
enum ShadowClickerApp {
    private static var controller: ShadowClickerController?

    static func run(duration: TimeInterval, encoder: JSONEncoder, emitJSON: Bool) throws {
        let config = try NativeCursorFollowConfig().validated()
        let app = NSApplication.shared
        app.setActivationPolicy(.accessory)

        let width = CGFloat(config.overlayDiameter + 112)
        let height = CGFloat(config.overlayDiameter + 34)
        let panel = ShadowPointerOverlayPanel(contentRect: NSRect(x: 0, y: 0, width: width, height: height))
        panel.contentView = ShadowClickerView(diameter: CGFloat(config.overlayDiameter))
        panel.orderFrontRegardless()

        controller = ShadowClickerController(
            app: app,
            panel: panel,
            config: config,
            encoder: encoder,
            emitJSON: emitJSON
        )
        controller?.start(duration: duration)
        app.run()
    }
}
#endif

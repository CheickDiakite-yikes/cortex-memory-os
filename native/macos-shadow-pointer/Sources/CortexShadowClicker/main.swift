import CortexShadowPointerNative
import Foundation

#if canImport(AppKit)
import AppKit
#endif

struct ShadowClickerArgs {
    var smoke = false
    var json = false
    var duration: TimeInterval = 15
    var agenticTitle = "Draft the next steps"
    var agenticMessage = "I see Color Page. I can draft the next safe steps."
    var agenticStatus = "draft only | display-only | no write"

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
            case "--agentic-title":
                guard let value = iterator.next(), !value.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
                    throw ShadowPointerNativeError.invalidControl("--agentic-title requires text")
                }
                agenticTitle = value
            case "--agentic-message":
                guard let value = iterator.next(), !value.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
                    throw ShadowPointerNativeError.invalidControl("--agentic-message requires text")
                }
                agenticMessage = value
            case "--agentic-status":
                guard let value = iterator.next(), !value.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
                    throw ShadowPointerNativeError.invalidControl("--agentic-status requires text")
                }
                agenticStatus = value
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
            let card = try NativeAgenticPointerCard(
                title: args.agenticTitle,
                message: args.agenticMessage,
                status: args.agenticStatus
            ).validated()
            try ShadowClickerApp.run(
                duration: args.duration,
                encoder: encoder,
                emitJSON: args.json,
                card: card
            )
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
final class LoadingDotsView: NSView {
    var phase: Double = 0 {
        didSet { needsDisplay = true }
    }

    override var isFlipped: Bool { true }

    override func draw(_ dirtyRect: NSRect) {
        NSColor.clear.setFill()
        dirtyRect.fill()

        for index in 0..<3 {
            let progress = (sin(phase + Double(index) * 0.85) + 1) / 2
            let alpha = 0.32 + 0.52 * progress
            let diameter = 5.0 + 1.6 * progress
            let x = 4.0 + Double(index) * 11.0
            let y = 9.0 - diameter / 2
            let dot = NSBezierPath(
                ovalIn: NSRect(x: x, y: y, width: diameter, height: diameter)
            )
            NSColor.systemBlue.withAlphaComponent(alpha).setFill()
            dot.fill()
        }
    }
}

@available(macOS 13.0, *)
@MainActor
final class ShadowClickerBubbleView: NSVisualEffectView {
    private let visualSpec: NativeOverlayVisualSpec
    private let card: NativeAgenticPointerCard
    private let titleField: NSTextField
    private let messageField: NSTextField
    private let statusField: NSTextField
    private let dotsView = LoadingDotsView(frame: NSRect(x: 0, y: 0, width: 44, height: 20))

    init(frame: NSRect, visualSpec: NativeOverlayVisualSpec, card: NativeAgenticPointerCard) {
        self.visualSpec = visualSpec
        self.card = card
        self.titleField = NSTextField(labelWithString: card.title)
        self.messageField = NSTextField(labelWithString: card.message)
        self.statusField = NSTextField(labelWithString: card.status)
        super.init(frame: frame)
        material = .hudWindow
        blendingMode = .behindWindow
        state = .active
        wantsLayer = true
        layer?.cornerRadius = visualSpec.bubbleCornerRadius
        layer?.cornerCurve = .continuous
        layer?.masksToBounds = false
        layer?.borderWidth = 0.75
        layer?.borderColor = NSColor.white.withAlphaComponent(0.30).cgColor
        layer?.shadowColor = NSColor.black.withAlphaComponent(0.22).cgColor
        layer?.shadowOpacity = 1
        layer?.shadowRadius = visualSpec.bubbleShadowRadius
        layer?.shadowOffset = NSSize(width: 0, height: -10)

        titleField.font = .systemFont(ofSize: 12, weight: .semibold)
        titleField.textColor = .labelColor
        titleField.lineBreakMode = .byTruncatingTail

        messageField.font = .systemFont(ofSize: 13, weight: .medium)
        messageField.textColor = .labelColor
        messageField.lineBreakMode = .byTruncatingTail
        messageField.maximumNumberOfLines = visualSpec.maxTextLines

        statusField.font = .systemFont(ofSize: 10, weight: .medium)
        statusField.textColor = .secondaryLabelColor
        statusField.lineBreakMode = .byTruncatingTail

        for view in [titleField, messageField, statusField, dotsView] {
            addSubview(view)
        }
    }

    required init?(coder: NSCoder) {
        nil
    }

    override var allowsVibrancy: Bool { visualSpec.vibrancyEnabled }

    override func layout() {
        super.layout()
        let inset: CGFloat = 14
        let titleHeight: CGFloat = 16
        let statusHeight: CGFloat = 14
        titleField.frame = NSRect(
            x: inset,
            y: bounds.height - inset - titleHeight,
            width: bounds.width - inset * 2 - 44,
            height: titleHeight
        )
        dotsView.frame = NSRect(
            x: bounds.width - inset - 40,
            y: bounds.height - inset - 18,
            width: 40,
            height: 18
        )
        messageField.frame = NSRect(
            x: inset,
            y: inset + statusHeight + 4,
            width: bounds.width - inset * 2,
            height: 22
        )
        statusField.frame = NSRect(
            x: inset,
            y: inset,
            width: bounds.width - inset * 2,
            height: statusHeight
        )
    }

    func update(phase: Double, bubbleSide: String) {
        dotsView.phase = phase
        messageField.stringValue = card.message
        statusField.stringValue = bubbleSide == "left"
            ? "\(card.status) | shifted left"
            : card.status
    }
}

@available(macOS 13.0, *)
@MainActor
final class ShadowClickerController {
    private let app: NSApplication
    private let panel: ShadowPointerOverlayPanel
    private let bubblePanel: ShadowPointerOverlayPanel
    private let bubbleView: ShadowClickerBubbleView
    private let config: NativeCursorFollowConfig
    private let visualSpec: NativeOverlayVisualSpec
    private let encoder: JSONEncoder
    private let emitJSON: Bool
    private var samples: [NativeCursorSample] = []
    private var followTimer: Timer?
    private var stopTimer: Timer?
    private var animationPhase: Double = 0

    init(
        app: NSApplication,
        panel: ShadowPointerOverlayPanel,
        bubblePanel: ShadowPointerOverlayPanel,
        bubbleView: ShadowClickerBubbleView,
        config: NativeCursorFollowConfig,
        visualSpec: NativeOverlayVisualSpec,
        encoder: JSONEncoder,
        emitJSON: Bool
    ) {
        self.app = app
        self.panel = panel
        self.bubblePanel = bubblePanel
        self.bubbleView = bubbleView
        self.config = config
        self.visualSpec = visualSpec
        self.encoder = encoder
        self.emitJSON = emitJSON
    }

    func start(duration: TimeInterval) {
        let interval = 1.0 / Double(config.sampleHz)
        let follow = Timer(timeInterval: interval, repeats: true) { [weak self] _ in
            Task { @MainActor in
                self?.tick()
            }
        }
        followTimer = follow
        RunLoop.main.add(follow, forMode: .common)

        let stop = Timer(timeInterval: duration, repeats: false) { [weak self] _ in
            Task { @MainActor in
                self?.finish()
            }
        }
        stopTimer = stop
        RunLoop.main.add(stop, forMode: .common)
    }

    private func tick() {
        let sample = NativeCursorProbe.sampleNow()
        samples.append(sample)
        let displayFrame = NativeDisplayFrame.containing(sample)
        let overlaySize = NativeOverlaySize(width: panel.frame.width, height: panel.frame.height)
        let bubbleSize = NativeBubbleSize(width: bubblePanel.frame.width, height: bubblePanel.frame.height)
        let placement = try? NativeCursorPlacementEngine.place(
            sample: sample,
            config: config,
            displayFrame: displayFrame,
            overlaySize: overlaySize,
            bubbleSize: bubbleSize
        )
        let nextOrigin = NSPoint(
            x: placement?.overlayOriginX ?? sample.x,
            y: placement?.overlayOriginY ?? sample.y
        )
        panel.setFrameOrigin(nextOrigin)
        if let placement {
            bubblePanel.setFrameOrigin(NSPoint(x: placement.bubbleX, y: placement.bubbleY))
            let phaseStep = (2.0 * Double.pi) / Double(visualSpec.loadingFrameRateHz)
            animationPhase += NSWorkspace.shared.accessibilityDisplayShouldReduceMotion
                ? 0
                : phaseStep
            bubbleView.update(phase: animationPhase, bubbleSide: placement.bubbleSide)
        }
        panel.contentView?.needsDisplay = true
        bubblePanel.contentView?.needsLayout = true
    }

    private func finish() {
        followTimer?.invalidate()
        stopTimer?.invalidate()
        let smokeSamples = samples.isEmpty ? [NativeCursorProbe.sampleNow()] : Array(samples.suffix(5))
        let result = try? NativeCursorFollowSmokeResult.run(samples: smokeSamples)
        panel.orderOut(nil)
        bubblePanel.orderOut(nil)
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

    static func run(
        duration: TimeInterval,
        encoder: JSONEncoder,
        emitJSON: Bool,
        card: NativeAgenticPointerCard
    ) throws {
        let config = try NativeCursorFollowConfig().validated()
        let visualSpec = try NativeOverlayVisualSpec().validated()
        let app = NSApplication.shared
        app.setActivationPolicy(.accessory)

        let width = CGFloat(config.overlayDiameter + 112)
        let height = CGFloat(config.overlayDiameter + 34)
        let panel = ShadowPointerOverlayPanel(contentRect: NSRect(x: 0, y: 0, width: width, height: height))
        panel.contentView = ShadowClickerView(diameter: CGFloat(config.overlayDiameter))
        panel.orderFrontRegardless()

        let bubbleFrame = NSRect(x: 0, y: 0, width: CGFloat(visualSpec.bubbleMaxWidth), height: 86)
        let bubblePanel = ShadowPointerOverlayPanel(contentRect: bubbleFrame)
        let bubbleView = ShadowClickerBubbleView(
            frame: bubbleFrame,
            visualSpec: visualSpec,
            card: card
        )
        bubblePanel.contentView = bubbleView
        bubblePanel.orderFrontRegardless()

        controller = ShadowClickerController(
            app: app,
            panel: panel,
            bubblePanel: bubblePanel,
            bubbleView: bubbleView,
            config: config,
            visualSpec: visualSpec,
            encoder: encoder,
            emitJSON: emitJSON
        )
        controller?.start(duration: duration)
        app.run()
    }
}
#endif

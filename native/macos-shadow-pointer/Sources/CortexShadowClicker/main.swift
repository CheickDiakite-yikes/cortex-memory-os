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
    var agenticCardFile: String?

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
            case "--agentic-card-file":
                guard let value = iterator.next(), !value.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
                    throw ShadowPointerNativeError.invalidControl("--agentic-card-file requires a path")
                }
                agenticCardFile = value
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
                card: card,
                cardFileURL: args.agenticCardFile.map { URL(fileURLWithPath: $0) }
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
import AppKit
import CoreVideo

public enum CompanionState: Sendable, Equatable {
    case idle
    case listening(pulsePhase: Double)
    case processing(pulsePhase: Double)
    case showingChip(text: String, expiration: Date, appearedAt: Date)
    case connectionError(message: String)
}

@available(macOS 13.0, *)
@MainActor
final class ShadowClickerView: NSView {
    private let diameter: CGFloat

    var companionState: CompanionState = .idle {
        didSet { needsDisplay = true }
    }

    var cursorLocation: NSPoint = NSPoint(x: 7, y: 58) {
        didSet { needsDisplay = true }
    }

    var audioAmplitude: CGFloat = 0 {
        didSet { needsDisplay = true }
    }

    init(diameter: CGFloat) {
        self.diameter = diameter
        // Make the view frame large enough to support the glowing circles and text chips without clipping.
        super.init(frame: NSRect(x: 0, y: 0, width: 600, height: 200))
        wantsLayer = true
    }

    required init?(coder: NSCoder) {
        nil
    }

    override func draw(_ dirtyRect: NSRect) {
        NSColor.clear.setFill()
        dirtyRect.fill()

        switch companionState {
        case .idle:
            break
        case .listening(let phase):
            drawListeningRing(at: cursorLocation, phase: phase, amplitude: audioAmplitude)
        case .processing(let phase):
            drawProcessingRing(at: cursorLocation, phase: phase)
        case .showingChip(let text, let expiration, let appearedAt):
            let progress = chipTransitionProgress(appearedAt: appearedAt, expiration: expiration)
            drawChip(text: text, at: cursorLocation, progress: progress, accent: .blue)
        case .connectionError(let message):
            drawConnectionError(at: cursorLocation, message: message)
        }
    }

    private func drawListeningRing(at center: NSPoint, phase: Double, amplitude: CGFloat) {
        let reactiveAmplitude = min(max(amplitude, 0), 1)
        let outerRadius: CGFloat = 12.0 + 3.0 * CGFloat(sin(phase)) + 16.0 * reactiveAmplitude
        let innerRadius: CGFloat = 6.0
        let ringWidth: CGFloat = 1.4 + 3.2 * reactiveAmplitude

        let outerRect = NSRect(
            x: center.x - outerRadius,
            y: center.y - outerRadius,
            width: outerRadius * 2,
            height: outerRadius * 2
        )
        let outerPath = NSBezierPath(ovalIn: outerRect)
        NSColor(calibratedRed: 0.0, green: 0.6, blue: 1.0, alpha: 0.18 + 0.20 * reactiveAmplitude).setFill()
        NSColor(calibratedRed: 0.0, green: 0.6, blue: 1.0, alpha: 0.72 + 0.24 * reactiveAmplitude).setStroke()
        outerPath.lineWidth = ringWidth
        outerPath.fill()
        outerPath.stroke()

        let innerRect = NSRect(
            x: center.x - innerRadius,
            y: center.y - innerRadius,
            width: innerRadius * 2,
            height: innerRadius * 2
        )
        let innerPath = NSBezierPath(ovalIn: innerRect)
        NSColor(calibratedRed: 0.0, green: 0.7, blue: 1.0, alpha: 0.95).setFill()
        innerPath.fill()
    }

    private func drawProcessingRing(at center: NSPoint, phase: Double) {
        let outerRadius: CGFloat = 11.0
        let innerRadius: CGFloat = 5.0

        let outerRect = NSRect(
            x: center.x - outerRadius,
            y: center.y - outerRadius,
            width: outerRadius * 2,
            height: outerRadius * 2
        )
        let outerPath = NSBezierPath(ovalIn: outerRect)

        let pulseOpacity = 0.4 + 0.3 * CGFloat(sin(phase * 1.5))
        NSColor(calibratedRed: 0.6, green: 0.2, blue: 0.9, alpha: pulseOpacity).setFill()
        NSColor(calibratedRed: 0.6, green: 0.2, blue: 0.9, alpha: 0.8).setStroke()
        outerPath.lineWidth = 1.5
        outerPath.fill()
        outerPath.stroke()

        let innerRect = NSRect(
            x: center.x - innerRadius,
            y: center.y - innerRadius,
            width: innerRadius * 2,
            height: innerRadius * 2
        )
        let innerPath = NSBezierPath(ovalIn: innerRect)
        NSColor(calibratedRed: 0.7, green: 0.3, blue: 1.0, alpha: 0.95).setFill()
        innerPath.fill()
    }

    private func drawConnectionError(at origin: NSPoint, message: String) {
        let pulse = 0.55 + 0.18 * CGFloat(sin(Date().timeIntervalSinceReferenceDate * 5))
        let radius: CGFloat = 13
        let rect = NSRect(x: origin.x - radius, y: origin.y - radius, width: radius * 2, height: radius * 2)
        let path = NSBezierPath(ovalIn: rect)
        NSColor.systemOrange.withAlphaComponent(0.18 + pulse * 0.12).setFill()
        NSColor.systemOrange.withAlphaComponent(0.72).setStroke()
        path.lineWidth = 2
        path.fill()
        path.stroke()
        drawChip(text: message, at: origin, progress: 1, accent: .amber)
    }

    private enum ChipAccent {
        case blue
        case amber
    }

    private func chipTransitionProgress(appearedAt: Date, expiration: Date) -> CGFloat {
        let age = Date().timeIntervalSince(appearedAt)
        let intro = min(max(age / 0.22, 0), 1)
        let outro = min(max(expiration.timeIntervalSinceNow / 0.28, 0), 1)
        return cubicEaseInOut(CGFloat(min(intro, outro)))
    }

    private func cubicEaseInOut(_ progress: CGFloat) -> CGFloat {
        let clamped = min(max(progress, 0), 1)
        if clamped < 0.5 {
            return 4 * clamped * clamped * clamped
        }
        let t = -2 * clamped + 2
        return 1 - (t * t * t) / 2
    }

    private func drawChip(text: String, at origin: NSPoint, progress: CGFloat, accent: ChipAccent) {
        let maxTextWidth: CGFloat = 360.0
        let paddingX: CGFloat = 16.0
        let paddingY: CGFloat = 10.0
        let font = NSFont.systemFont(ofSize: 13, weight: .medium)
        let paragraphStyle = NSMutableParagraphStyle()
        paragraphStyle.lineBreakMode = .byWordWrapping

        let attrs: [NSAttributedString.Key: Any] = [
            .font: font,
            .foregroundColor: NSColor.white,
            .paragraphStyle: paragraphStyle
        ]

        let constraintRect = CGSize(width: maxTextWidth, height: .greatestFiniteMagnitude)
        let boundingBox = text.boundingRect(
            with: constraintRect,
            options: [.usesLineFragmentOrigin, .usesFontLeading],
            attributes: attrs,
            context: nil
        )

        let textWidth = ceil(boundingBox.width)
        let textHeight = ceil(boundingBox.height)

        let bubbleWidth = textWidth + paddingX * 2
        let bubbleHeight = textHeight + paddingY * 2

        let rect = clampedChipRect(
            origin: origin,
            bubbleWidth: bubbleWidth,
            bubbleHeight: bubbleHeight
        )

        let scale = 0.94 + 0.06 * progress
        let scaledRect = rect.insetBy(
            dx: rect.width * (1 - scale) / 2,
            dy: rect.height * (1 - scale) / 2
        )
        let path = NSBezierPath(roundedRect: scaledRect, xRadius: 12, yRadius: 12)
        let fillColor = accent == .amber
            ? NSColor(calibratedRed: 0.16, green: 0.10, blue: 0.04, alpha: 0.88 * progress)
            : NSColor(calibratedWhite: 0.07, alpha: 0.88 * progress)
        fillColor.setFill()

        let shadow = NSShadow()
        shadow.shadowBlurRadius = 16
        shadow.shadowOffset = NSSize(width: 0, height: -6)
        shadow.shadowColor = NSColor.black.withAlphaComponent(0.4)

        NSGraphicsContext.saveGraphicsState()
        shadow.set()
        path.fill()
        NSGraphicsContext.restoreGraphicsState()

        let strokeColor = accent == .amber
            ? NSColor.systemOrange.withAlphaComponent(0.46 * progress)
            : NSColor(calibratedWhite: 1.0, alpha: 0.22 * progress)
        strokeColor.setStroke()
        path.lineWidth = 1.0
        path.stroke()

        let textRect = NSRect(
            x: rect.origin.x + paddingX,
            y: rect.origin.y + paddingY,
            width: textWidth,
            height: textHeight
        )
        NSGraphicsContext.saveGraphicsState()
        NSGraphicsContext.current?.cgContext.setAlpha(progress)
        text.draw(in: textRect, withAttributes: attrs)
        NSGraphicsContext.restoreGraphicsState()
    }

    private func clampedChipRect(origin: NSPoint, bubbleWidth: CGFloat, bubbleHeight: CGFloat) -> NSRect {
        let windowOrigin = window?.frame.origin ?? .zero
        let visibleFrame = window?.screen?.visibleFrame ?? NSScreen.main?.visibleFrame
        guard let visibleFrame else {
            let fitsRight = (origin.x + 20 + bubbleWidth) <= bounds.width
            let rawX = fitsRight ? (origin.x + 20) : (origin.x - 20 - bubbleWidth)
            return NSRect(
                x: min(max(rawX, 8), max(8, bounds.width - bubbleWidth - 8)),
                y: min(max(origin.y - bubbleHeight / 2, 8), max(8, bounds.height - bubbleHeight - 8)),
                width: bubbleWidth,
                height: bubbleHeight
            )
        }

        let globalPlacement = NativeChipPlacementEngine.place(
            cursorX: Double(windowOrigin.x + origin.x),
            cursorY: Double(windowOrigin.y + origin.y),
            chipWidth: Double(bubbleWidth),
            chipHeight: Double(bubbleHeight),
            visibleFrame: NativeDisplayFrame(
                minX: visibleFrame.minX,
                minY: visibleFrame.minY,
                width: visibleFrame.width,
                height: visibleFrame.height
            )
        )
        return NSRect(
            x: CGFloat(globalPlacement.x) - windowOrigin.x,
            y: CGFloat(globalPlacement.y) - windowOrigin.y,
            width: CGFloat(globalPlacement.width),
            height: CGFloat(globalPlacement.height)
        )
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
    private var card: NativeAgenticPointerCard
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
        titleField.stringValue = card.title
        messageField.stringValue = card.message
        statusField.stringValue = bubbleSide == "left"
            ? "\(card.status) | shifted left"
            : card.status
    }

    func apply(card nextCard: NativeAgenticPointerCard) {
        card = nextCard
        needsLayout = true
        needsDisplay = true
    }
}

struct AgenticCardFilePayload: Decodable {
    var title: String
    var message: String
    var status: String
}

@available(macOS 13.0, *)
@MainActor
final class DisplayLinkDriver {
    private var displayLink: CVDisplayLink?
    private let onFrame: @MainActor () -> Void

    init(onFrame: @escaping @MainActor () -> Void) {
        self.onFrame = onFrame
    }

    func start() {
        guard displayLink == nil else { return }
        var link: CVDisplayLink?
        guard CVDisplayLinkCreateWithActiveCGDisplays(&link) == kCVReturnSuccess,
              let link
        else {
            return
        }
        let callback: CVDisplayLinkOutputCallback = { _, _, _, _, _, context in
            guard let context else {
                return kCVReturnSuccess
            }
            let driver = Unmanaged<DisplayLinkDriver>.fromOpaque(context).takeUnretainedValue()
            Task { @MainActor in
                driver.onFrame()
            }
            return kCVReturnSuccess
        }
        CVDisplayLinkSetOutputCallback(
            link,
            callback,
            Unmanaged.passUnretained(self).toOpaque()
        )
        CVDisplayLinkStart(link)
        displayLink = link
    }

    func stop() {
        guard let displayLink else { return }
        CVDisplayLinkStop(displayLink)
        self.displayLink = nil
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
    private let cardFileURL: URL?
    private var samples: [NativeCursorSample] = []
    private var displayLinkDriver: DisplayLinkDriver?
    private var stopTimer: Timer?
    private var lastCardPoll: Date?
    private var lastCardFileModificationDate: Date?

    private var companionState: CompanionState = .idle
    private var streamedText: String = ""
    private var audioAmplitude: CGFloat = 0

    init(
        app: NSApplication,
        panel: ShadowPointerOverlayPanel,
        bubblePanel: ShadowPointerOverlayPanel,
        bubbleView: ShadowClickerBubbleView,
        config: NativeCursorFollowConfig,
        visualSpec: NativeOverlayVisualSpec,
        encoder: JSONEncoder,
        emitJSON: Bool,
        cardFileURL: URL?
    ) {
        self.app = app
        self.panel = panel
        self.bubblePanel = bubblePanel
        self.bubbleView = bubbleView
        self.config = config
        self.visualSpec = visualSpec
        self.encoder = encoder
        self.emitJSON = emitJSON
        self.cardFileURL = cardFileURL

        setupNotificationObservers()
        setupRealtimeVoiceCallbacks()
    }

    private func setupNotificationObservers() {
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleTextDeltaNotification(_:)),
            name: Notification.Name("RealtimeTextDeltaReceived"),
            object: nil
        )
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleTextDoneNotification(_:)),
            name: Notification.Name("RealtimeTextDoneReceived"),
            object: nil
        )
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleAudioAmplitudeNotification(_:)),
            name: .realtimeAudioAmplitudeUpdated,
            object: nil
        )
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleConnectionErrorNotification(_:)),
            name: .realtimeConnectionError,
            object: nil
        )
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleConnectionRestoredNotification(_:)),
            name: .realtimeConnectionRestored,
            object: nil
        )
    }

    private func setupRealtimeVoiceCallbacks() {
        RealtimeVoiceClient.shared.onToolCallReceived = { [weak self] name, callId, args in
            Task { @MainActor in
                self?.handleToolCall(name: name, callId: callId, arguments: args)
            }
        }
    }

    func start(duration: TimeInterval) {
        let driver = DisplayLinkDriver { [weak self] in
            self?.tick()
        }
        displayLinkDriver = driver
        driver.start()

        let stop = Timer(timeInterval: duration, repeats: false) { [weak self] _ in
            Task { @MainActor in
                self?.finish()
            }
        }
        stopTimer = stop
        RunLoop.main.add(stop, forMode: .common)
    }

    private func tick() {
        refreshAgenticCardIfNeeded()
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

        // Update dynamic companion state from PTT (modifier key polling)
        let isControlPressed = NSEvent.modifierFlags.contains(.control)

        switch companionState {
        case .idle, .showingChip:
            if isControlPressed {
                streamedText = ""
                companionState = .listening(pulsePhase: 0.0)
                RealtimeVoiceClient.shared.startListening()
            } else if case .showingChip(_, let expiration, _) = companionState, Date() > expiration {
                companionState = .idle
            }
        case .listening(let phase):
            if isControlPressed {
                companionState = .listening(pulsePhase: phase + 0.1)
            } else {
                RealtimeVoiceClient.shared.stopListening()
                companionState = .processing(pulsePhase: 0.0)
            }
        case .processing(let phase):
            companionState = .processing(pulsePhase: phase + 0.1)
        case .connectionError:
            if isControlPressed {
                companionState = .listening(pulsePhase: 0.0)
                RealtimeVoiceClient.shared.startListening()
            }
        }

        // Pass cursor location and companion state to view
        let currentMouse = NSEvent.mouseLocation
        let cursorX = currentMouse.x - panel.frame.origin.x
        let cursorY = currentMouse.y - panel.frame.origin.y

        if let view = panel.contentView as? ShadowClickerView {
            view.cursorLocation = NSPoint(x: cursorX, y: cursorY)
            view.audioAmplitude = audioAmplitude
            view.companionState = companionState
        }

        panel.contentView?.needsDisplay = true
    }

    private func refreshAgenticCardIfNeeded() {
        guard let cardFileURL else {
            return
        }
        let now = Date()
        if let lastCardPoll, now.timeIntervalSince(lastCardPoll) < 0.25 {
            return
        }
        lastCardPoll = now
        guard let attributes = try? FileManager.default.attributesOfItem(atPath: cardFileURL.path),
              let modificationDate = attributes[.modificationDate] as? Date
        else {
            return
        }
        if let lastCardFileModificationDate, modificationDate <= lastCardFileModificationDate {
            return
        }
        guard let data = try? Data(contentsOf: cardFileURL),
              let payload = try? JSONDecoder().decode(AgenticCardFilePayload.self, from: data),
              let card = try? NativeAgenticPointerCard(
                  title: payload.title,
                  message: payload.message,
                  status: payload.status
              ).validated()
        else {
            return
        }
        lastCardFileModificationDate = modificationDate
        bubbleView.apply(card: card)
    }

    private func finish() {
        displayLinkDriver?.stop()
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

    @objc private func handleTextDeltaNotification(_ notification: Notification) {
        guard let userInfo = notification.userInfo, let delta = userInfo["delta"] as? String else { return }
        streamedText += delta
        showChip(text: streamedText)
    }

    @objc private func handleTextDoneNotification(_ notification: Notification) {
        guard let userInfo = notification.userInfo, let text = userInfo["text"] as? String else { return }
        streamedText = text
        showChip(text: text)
    }

    private func showChip(text: String) {
        companionState = .showingChip(
            text: text,
            expiration: Date().addingTimeInterval(4.0),
            appearedAt: Date()
        )
        if let view = panel.contentView as? ShadowClickerView {
            view.companionState = companionState
        }
    }

    @objc private func handleAudioAmplitudeNotification(_ notification: Notification) {
        guard let amplitude = notification.userInfo?["amplitude"] as? Float else { return }
        audioAmplitude = CGFloat(min(max(amplitude * 3.2, 0), 1))
        if let view = panel.contentView as? ShadowClickerView {
            view.audioAmplitude = audioAmplitude
        }
    }

    @objc private func handleConnectionErrorNotification(_ notification: Notification) {
        let message = notification.userInfo?["message"] as? String ?? "Realtime connection unavailable"
        companionState = .connectionError(message: "Connection issue: \(message)")
        if let view = panel.contentView as? ShadowClickerView {
            view.companionState = companionState
        }
    }

    @objc private func handleConnectionRestoredNotification(_ notification: Notification) {
        if case .connectionError = companionState {
            companionState = .idle
        }
        if let view = panel.contentView as? ShadowClickerView {
            view.companionState = companionState
        }
    }

    private func handleToolCall(name: String, callId: String, arguments: [String: Any]) {
        if name == "explain_target" {
            let targetId = arguments["target_id"] as? String ?? "unknown"
            showChip(text: "Explaining target: \(targetId)")
            RealtimeVoiceClient.shared.sendToolOutput(
                callId: callId,
                output: ["status": "success", "message": "Target \(targetId) explained successfully."]
            )
        } else if name == "move_mouse" {
            guard let x = arguments["x"] as? Double, let y = arguments["y"] as? Double else {
                RealtimeVoiceClient.shared.sendToolOutput(
                    callId: callId,
                    output: ["status": "error", "message": "Missing coordinates (x, y)"]
                )
                return
            }
            showChip(text: "Moving pointer natively to (\(Int(x)), \(Int(y)))")
            executeMoveMouse(x: x, y: y)
            RealtimeVoiceClient.shared.sendToolOutput(
                callId: callId,
                output: ["status": "success", "x": x, "y": y]
            )
        } else if name == "click_mouse" {
            let x = arguments["x"] as? Double
            let y = arguments["y"] as? Double
            if let x = x, let y = y {
                showChip(text: "Clicking natively at (\(Int(x)), \(Int(y)))")
            } else {
                showChip(text: "Clicking natively")
            }
            executeClickMouse(x: x, y: y)
            RealtimeVoiceClient.shared.sendToolOutput(
                callId: callId,
                output: ["status": "success"]
            )
        } else if name == "right_click_mouse" {
            guard let x = arguments["x"] as? Double, let y = arguments["y"] as? Double else {
                sendToolArgumentError(callId: callId, message: "Missing coordinates (x, y)")
                return
            }
            showChip(text: "Right-clicking at (\(Int(x)), \(Int(y)))")
            executeMouseClick(x: x, y: y, button: .right, clickCount: 1)
            RealtimeVoiceClient.shared.sendToolOutput(callId: callId, output: ["status": "success"])
        } else if name == "double_click_mouse" {
            guard let x = arguments["x"] as? Double, let y = arguments["y"] as? Double else {
                sendToolArgumentError(callId: callId, message: "Missing coordinates (x, y)")
                return
            }
            showChip(text: "Double-clicking at (\(Int(x)), \(Int(y)))")
            executeMouseClick(x: x, y: y, button: .left, clickCount: 2)
            RealtimeVoiceClient.shared.sendToolOutput(callId: callId, output: ["status": "success"])
        } else if name == "drag_mouse" {
            guard let fromX = arguments["fromX"] as? Double,
                  let fromY = arguments["fromY"] as? Double,
                  let toX = arguments["toX"] as? Double,
                  let toY = arguments["toY"] as? Double
            else {
                sendToolArgumentError(callId: callId, message: "Missing drag coordinates")
                return
            }
            showChip(text: "Dragging from (\(Int(fromX)), \(Int(fromY))) to (\(Int(toX)), \(Int(toY)))")
            executeDragMouse(fromX: fromX, fromY: fromY, toX: toX, toY: toY)
            RealtimeVoiceClient.shared.sendToolOutput(callId: callId, output: ["status": "success"])
        } else if name == "scroll_mouse" {
            guard let dx = arguments["dx"] as? Double, let dy = arguments["dy"] as? Double else {
                sendToolArgumentError(callId: callId, message: "Missing scroll deltas")
                return
            }
            showChip(text: "Scrolling")
            executeScrollMouse(dx: dx, dy: dy)
            RealtimeVoiceClient.shared.sendToolOutput(callId: callId, output: ["status": "success"])
        }
    }

    private func sendToolArgumentError(callId: String, message: String) {
        RealtimeVoiceClient.shared.sendToolOutput(
            callId: callId,
            output: ["status": "error", "message": message]
        )
    }

    private func convertToCGSpace(x: Double, y: Double) -> CGPoint {
        let screenHeight = Double(NSScreen.screens.first?.frame.height ?? 1080.0)
        let visible = NSScreen.screens.first?.visibleFrame
        let minX = Double(visible?.minX ?? 0)
        let maxX = Double(visible?.maxX ?? CGFloat.greatestFiniteMagnitude)
        let minY = Double(visible?.minY ?? 0)
        let maxY = Double(visible?.maxY ?? CGFloat(screenHeight))
        let clampedX = min(max(x, minX), maxX)
        let clampedY = min(max(y, minY), maxY)
        return CGPoint(x: clampedX, y: screenHeight - clampedY)
    }

    private func executeMoveMouse(x: Double, y: Double) {
        let cgPoint = convertToCGSpace(x: x, y: y)
        CGWarpMouseCursorPosition(cgPoint)
        if let source = CGEventSource(stateID: .combinedSessionState),
           let moveEvent = CGEvent(mouseEventSource: source, mouseType: .mouseMoved, mouseCursorPosition: cgPoint, mouseButton: .left) {
            moveEvent.post(tap: .cghidEventTap)
        }
    }

    private func executeClickMouse(x: Double?, y: Double?) {
        let cgPoint: CGPoint
        if let x = x, let y = y {
            cgPoint = convertToCGSpace(x: x, y: y)
        } else {
            let currentAppKit = NSEvent.mouseLocation
            cgPoint = convertToCGSpace(x: currentAppKit.x, y: currentAppKit.y)
        }
        postMouseClick(at: cgPoint, button: .left, clickCount: 1)
    }

    private func executeMouseClick(x: Double, y: Double, button: CGMouseButton, clickCount: Int) {
        let cgPoint = convertToCGSpace(x: x, y: y)
        postMouseClick(at: cgPoint, button: button, clickCount: clickCount)
    }

    private func postMouseClick(at point: CGPoint, button: CGMouseButton, clickCount: Int) {
        CGWarpMouseCursorPosition(point)
        let source = CGEventSource(stateID: .combinedSessionState)
        let downType: CGEventType = button == .right ? .rightMouseDown : .leftMouseDown
        let upType: CGEventType = button == .right ? .rightMouseUp : .leftMouseUp
        let taps = max(1, clickCount)
        for tapIndex in 1...taps {
            guard let down = CGEvent(
                mouseEventSource: source,
                mouseType: downType,
                mouseCursorPosition: point,
                mouseButton: button
            ),
            let up = CGEvent(
                mouseEventSource: source,
                mouseType: upType,
                mouseCursorPosition: point,
                mouseButton: button
            ) else {
                print("Failed to create mouse click event")
                return
            }
            down.setIntegerValueField(.mouseEventClickState, value: Int64(min(tapIndex, 2)))
            up.setIntegerValueField(.mouseEventClickState, value: Int64(min(tapIndex, 2)))
            down.post(tap: .cghidEventTap)
            usleep(35_000)
            up.post(tap: .cghidEventTap)
            usleep(55_000)
        }
    }

    private func executeDragMouse(fromX: Double, fromY: Double, toX: Double, toY: Double) {
        let start = convertToCGSpace(x: fromX, y: fromY)
        let end = convertToCGSpace(x: toX, y: toY)
        CGWarpMouseCursorPosition(start)
        let source = CGEventSource(stateID: .combinedSessionState)
        guard let down = CGEvent(
            mouseEventSource: source,
            mouseType: .leftMouseDown,
            mouseCursorPosition: start,
            mouseButton: .left
        ) else {
            return
        }
        down.post(tap: .cghidEventTap)
        let steps = 18
        for step in 1...steps {
            let progress = CGFloat(step) / CGFloat(steps)
            let point = CGPoint(
                x: start.x + (end.x - start.x) * progress,
                y: start.y + (end.y - start.y) * progress
            )
            CGWarpMouseCursorPosition(point)
            if let dragged = CGEvent(
                mouseEventSource: source,
                mouseType: .leftMouseDragged,
                mouseCursorPosition: point,
                mouseButton: .left
            ) {
                dragged.post(tap: .cghidEventTap)
            }
            usleep(10_000)
        }
        if let up = CGEvent(
            mouseEventSource: source,
            mouseType: .leftMouseUp,
            mouseCursorPosition: end,
            mouseButton: .left
        ) {
            up.post(tap: .cghidEventTap)
        }
    }

    private func executeScrollMouse(dx: Double, dy: Double) {
        let source = CGEventSource(stateID: .combinedSessionState)
        let scrollX = Int32(min(max(dx, Double(Int32.min)), Double(Int32.max)))
        let scrollY = Int32(min(max(dy, Double(Int32.min)), Double(Int32.max)))
        if let event = CGEvent(
            scrollWheelEvent2Source: source,
            units: .pixel,
            wheelCount: 2,
            wheel1: scrollY,
            wheel2: scrollX,
            wheel3: 0
        ) {
            event.post(tap: CGEventTapLocation.cghidEventTap)
        }
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
        card: NativeAgenticPointerCard,
        cardFileURL: URL?
    ) throws {
        let config = try NativeCursorFollowConfig().validated()
        let visualSpec = try NativeOverlayVisualSpec().validated()
        let app = NSApplication.shared
        app.setActivationPolicy(.accessory)

        // Make overlay panel dimension large (600x200) to host our beautiful dynamic text chips.
        let width = CGFloat(600)
        let height = CGFloat(200)
        let panel = ShadowPointerOverlayPanel(contentRect: NSRect(x: 0, y: 0, width: width, height: height))
        panel.contentView = ShadowClickerView(diameter: CGFloat(config.overlayDiameter))
        panel.orderFrontRegardless()

        // Setup hidden secondary bubble panel as backup/legacy requirement
        let bubbleFrame = NSRect.zero
        let bubblePanel = ShadowPointerOverlayPanel(contentRect: bubbleFrame)
        let bubbleView = ShadowClickerBubbleView(
            frame: bubbleFrame,
            visualSpec: visualSpec,
            card: card
        )
        bubblePanel.contentView = bubbleView

        RealtimeVoiceClient.shared.fetchTokenAndConnect { success, error in
            if success {
                print("Connected to RealtimeVoiceClient!")
            } else {
                print("Failed to connect: \(error ?? "Unknown")")
            }
        }

        controller = ShadowClickerController(
            app: app,
            panel: panel,
            bubblePanel: bubblePanel,
            bubbleView: bubbleView,
            config: config,
            visualSpec: visualSpec,
            encoder: encoder,
            emitJSON: emitJSON,
            cardFileURL: cardFileURL
        )
        controller?.start(duration: duration)
        app.run()
    }
}
#endif

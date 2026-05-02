import Foundation

#if canImport(AppKit)
import AppKit
#endif
#if canImport(ApplicationServices)
@preconcurrency import ApplicationServices
#endif
#if canImport(CoreGraphics)
import CoreGraphics
#endif

public let shadowPointerNativePolicyRef = "policy_shadow_pointer_native_overlay_v1"
public let nativeCapturePermissionSmokeBenchmarkID = "NATIVE-CAPTURE-PERMISSION-SMOKE-001"
public let nativeCapturePermissionSmokePolicyRef = "policy_native_capture_permission_smoke_v1"
public let nativeCursorFollowBenchmarkID = "NATIVE-CURSOR-FOLLOW-001"
public let nativeCursorFollowPolicyRef = "policy_native_cursor_follow_v1"
public let nativeScreenCaptureProbeBenchmarkID = "NATIVE-SCREEN-CAPTURE-PROBE-001"
public let nativeScreenCaptureProbePolicyRef = "policy_native_screen_capture_probe_v1"

public enum ShadowPointerNativeState: String, Codable, CaseIterable, Sendable {
    case off
    case observing
    case privateMasking = "private_masking"
    case remembering
    case agentContexting = "agent_contexting"
    case needsApproval = "needs_approval"
    case paused
}

public enum ShadowPointerNativeControlAction: String, Codable, Sendable {
    case status
    case pauseObservation = "pause_observation"
    case resumeObservation = "resume_observation"
    case deleteRecent = "delete_recent"
    case ignoreApp = "ignore_app"
}

public struct NativeOverlayWindowSpec: Codable, Equatable, Sendable {
    public var policyRef: String
    public var level: String
    public var styleMasks: [String]
    public var collectionBehaviors: [String]
    public var isOpaque: Bool
    public var backgroundColor: String
    public var ignoresMouseEventsByDefault: Bool
    public var canBecomeKey: Bool
    public var canBecomeMain: Bool
    public var hasShadow: Bool
    public var accessibilityLabel: String

    public static let shadowPointerDefault = NativeOverlayWindowSpec(
        policyRef: shadowPointerNativePolicyRef,
        level: "floating",
        styleMasks: ["nonactivatingPanel", "borderless"],
        collectionBehaviors: ["canJoinAllSpaces", "fullScreenAuxiliary", "stationary"],
        isOpaque: false,
        backgroundColor: "clear",
        ignoresMouseEventsByDefault: true,
        canBecomeKey: false,
        canBecomeMain: false,
        hasShadow: false,
        accessibilityLabel: "Cortex Shadow Pointer"
    )
}

public struct ShadowPointerNativeSnapshot: Codable, Equatable, Sendable {
    public var state: ShadowPointerNativeState
    public var workstreamLabel: String
    public var seeing: [String]
    public var ignoring: [String]
    public var possibleMemory: String?
    public var possibleSkill: String?
    public var approvalReason: String?

    public init(
        state: ShadowPointerNativeState,
        workstreamLabel: String,
        seeing: [String] = [],
        ignoring: [String] = [],
        possibleMemory: String? = nil,
        possibleSkill: String? = nil,
        approvalReason: String? = nil
    ) {
        self.state = state
        self.workstreamLabel = workstreamLabel
        self.seeing = seeing
        self.ignoring = ignoring
        self.possibleMemory = possibleMemory
        self.possibleSkill = possibleSkill
        self.approvalReason = approvalReason
    }

    public static let observingDefault = ShadowPointerNativeSnapshot(
        state: .observing,
        workstreamLabel: "Debugging auth flow",
        seeing: ["VS Code", "Terminal", "Chrome"],
        ignoring: ["password fields", "private messages"],
        possibleMemory: "Auth bug reproduction flow",
        possibleSkill: "Frontend auth debugging"
    )
}

public struct ShadowPointerNativeControlReceipt: Codable, Equatable, Sendable {
    public var action: ShadowPointerNativeControlAction
    public var resultingSnapshot: ShadowPointerNativeSnapshot
    public var observationActive: Bool
    public var memoryWriteAllowed: Bool
    public var auditRequired: Bool
    public var auditAction: String?
    public var confirmationObserved: Bool
    public var affectedApps: [String]
    public var deletedWindowMinutes: Int?
    public var safetyNotes: [String]
}

public enum ShadowPointerNativeControlBridge {
    public static func apply(
        snapshot: ShadowPointerNativeSnapshot,
        action: ShadowPointerNativeControlAction,
        durationMinutes: Int? = nil,
        deleteWindowMinutes: Int? = nil,
        appName: String? = nil,
        userConfirmed: Bool = false
    ) throws -> ShadowPointerNativeControlReceipt {
        switch action {
        case .status:
            return ShadowPointerNativeControlReceipt(
                action: action,
                resultingSnapshot: snapshot,
                observationActive: observationActive(snapshot.state),
                memoryWriteAllowed: memoryWriteAllowed(snapshot.state),
                auditRequired: false,
                auditAction: nil,
                confirmationObserved: userConfirmed,
                affectedApps: [],
                deletedWindowMinutes: nil,
                safetyNotes: ["status is read-only"]
            )

        case .pauseObservation:
            guard let durationMinutes, durationMinutes > 0 else {
                throw ShadowPointerNativeError.invalidControl("pause requires durationMinutes")
            }
            let paused = ShadowPointerNativeSnapshot(
                state: .paused,
                workstreamLabel: "Paused for \(durationMinutes) min",
                seeing: [],
                ignoring: ["all observation until resume or timeout"],
                possibleSkill: snapshot.possibleSkill
            )
            return ShadowPointerNativeControlReceipt(
                action: action,
                resultingSnapshot: paused,
                observationActive: false,
                memoryWriteAllowed: false,
                auditRequired: true,
                auditAction: "pause_observation",
                confirmationObserved: userConfirmed,
                affectedApps: [],
                deletedWindowMinutes: nil,
                safetyNotes: ["observation disabled", "memory writes blocked while paused"]
            )

        case .resumeObservation:
            let resumed = ShadowPointerNativeSnapshot(
                state: .observing,
                workstreamLabel: "Observation resumed",
                seeing: snapshot.seeing.isEmpty ? ["authorized apps"] : snapshot.seeing,
                ignoring: snapshot.ignoring,
                possibleMemory: snapshot.possibleMemory,
                possibleSkill: snapshot.possibleSkill
            )
            return ShadowPointerNativeControlReceipt(
                action: action,
                resultingSnapshot: resumed,
                observationActive: true,
                memoryWriteAllowed: true,
                auditRequired: true,
                auditAction: "resume_observation",
                confirmationObserved: userConfirmed,
                affectedApps: [],
                deletedWindowMinutes: nil,
                safetyNotes: ["observation resumed within current consent scope"]
            )

        case .deleteRecent:
            guard userConfirmed else {
                throw ShadowPointerNativeError.invalidControl(
                    "delete recent requires explicit confirmation"
                )
            }
            guard let deleteWindowMinutes, deleteWindowMinutes > 0 else {
                throw ShadowPointerNativeError.invalidControl(
                    "delete recent requires deleteWindowMinutes"
                )
            }
            let deleted = ShadowPointerNativeSnapshot(
                state: .privateMasking,
                workstreamLabel: "Recent observation deletion",
                seeing: [],
                ignoring: ["last \(deleteWindowMinutes) minutes"],
                possibleSkill: snapshot.possibleSkill
            )
            return ShadowPointerNativeControlReceipt(
                action: action,
                resultingSnapshot: deleted,
                observationActive: observationActive(snapshot.state),
                memoryWriteAllowed: false,
                auditRequired: true,
                auditAction: "delete_recent_observation",
                confirmationObserved: true,
                affectedApps: [],
                deletedWindowMinutes: deleteWindowMinutes,
                safetyNotes: [
                    "raw and derived observations in the selected window must be deleted or tombstoned",
                    "new memory writes are blocked until deletion completes",
                ]
            )

        case .ignoreApp:
            guard userConfirmed else {
                throw ShadowPointerNativeError.invalidControl(
                    "ignore app requires explicit confirmation"
                )
            }
            guard let appName, !appName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else {
                throw ShadowPointerNativeError.invalidControl("ignore app requires appName")
            }
            let cleanAppName = appName.trimmingCharacters(in: .whitespacesAndNewlines)
            let ignored = ShadowPointerNativeSnapshot(
                state: .privateMasking,
                workstreamLabel: "Ignoring \(cleanAppName)",
                seeing: snapshot.seeing.filter { $0 != cleanAppName },
                ignoring: appendUnique(snapshot.ignoring, cleanAppName),
                possibleMemory: snapshot.possibleMemory,
                possibleSkill: snapshot.possibleSkill
            )
            return ShadowPointerNativeControlReceipt(
                action: action,
                resultingSnapshot: ignored,
                observationActive: observationActive(snapshot.state),
                memoryWriteAllowed: false,
                auditRequired: true,
                auditAction: "ignore_app_observation",
                confirmationObserved: true,
                affectedApps: [cleanAppName],
                deletedWindowMinutes: nil,
                safetyNotes: [
                    "ignored app must be excluded from capture adapters",
                    "memory writes from ignored app are blocked",
                ]
            )
        }
    }

    public static func memoryWriteAllowed(_ state: ShadowPointerNativeState) -> Bool {
        switch state {
        case .off, .paused, .privateMasking, .needsApproval:
            return false
        case .observing, .remembering, .agentContexting:
            return true
        }
    }

    public static func observationActive(_ state: ShadowPointerNativeState) -> Bool {
        switch state {
        case .off, .paused:
            return false
        case .observing, .privateMasking, .remembering, .agentContexting, .needsApproval:
            return true
        }
    }
}

public enum ShadowPointerNativeError: Error, Equatable, CustomStringConvertible {
    case invalidControl(String)

    public var description: String {
        switch self {
        case .invalidControl(let message):
            return message
        }
    }
}

public struct ShadowPointerNativeSmokeResult: Codable, Equatable, Sendable {
    public var policyRef: String
    public var overlaySpec: NativeOverlayWindowSpec
    public var pauseBlocksMemory: Bool
    public var deleteRecentBlocksMemory: Bool
    public var ignoreAppBlocksMemory: Bool
    public var displayOnlyPointing: Bool
    public var passed: Bool

    public static func run() throws -> ShadowPointerNativeSmokeResult {
        let snapshot = ShadowPointerNativeSnapshot.observingDefault
        let pause = try ShadowPointerNativeControlBridge.apply(
            snapshot: snapshot,
            action: .pauseObservation,
            durationMinutes: 60
        )
        let deleteRecent = try ShadowPointerNativeControlBridge.apply(
            snapshot: snapshot,
            action: .deleteRecent,
            deleteWindowMinutes: 10,
            userConfirmed: true
        )
        let ignoreApp = try ShadowPointerNativeControlBridge.apply(
            snapshot: snapshot,
            action: .ignoreApp,
            appName: "Chrome",
            userConfirmed: true
        )
        let spec = NativeOverlayWindowSpec.shadowPointerDefault
        let displayOnlyPointing = spec.ignoresMouseEventsByDefault && !spec.canBecomeKey
        let passed = !pause.memoryWriteAllowed
            && !deleteRecent.memoryWriteAllowed
            && !ignoreApp.memoryWriteAllowed
            && displayOnlyPointing
            && spec.policyRef == shadowPointerNativePolicyRef
        return ShadowPointerNativeSmokeResult(
            policyRef: shadowPointerNativePolicyRef,
            overlaySpec: spec,
            pauseBlocksMemory: !pause.memoryWriteAllowed,
            deleteRecentBlocksMemory: !deleteRecent.memoryWriteAllowed,
            ignoreAppBlocksMemory: !ignoreApp.memoryWriteAllowed,
            displayOnlyPointing: displayOnlyPointing,
            passed: passed
        )
    }
}

public struct NativeCapturePermissionProbe: Equatable, Sendable {
    public var screenRecordingPreflight: Bool
    public var accessibilityTrusted: Bool
    public var promptRequested: Bool

    public init(
        screenRecordingPreflight: Bool,
        accessibilityTrusted: Bool,
        promptRequested: Bool
    ) {
        self.screenRecordingPreflight = screenRecordingPreflight
        self.accessibilityTrusted = accessibilityTrusted
        self.promptRequested = promptRequested
    }

    public static func readCurrentProcess() -> NativeCapturePermissionProbe {
        #if canImport(CoreGraphics)
        let screenRecordingPreflight = CGPreflightScreenCaptureAccess()
        #else
        let screenRecordingPreflight = false
        #endif

        #if canImport(ApplicationServices)
        let options = [
            kAXTrustedCheckOptionPrompt.takeUnretainedValue() as String: false
        ] as CFDictionary
        let accessibilityTrusted = AXIsProcessTrustedWithOptions(options)
        #else
        let accessibilityTrusted = false
        #endif

        return NativeCapturePermissionProbe(
            screenRecordingPreflight: screenRecordingPreflight,
            accessibilityTrusted: accessibilityTrusted,
            promptRequested: false
        )
    }
}

public struct NativeCapturePermissionSmokeResult: Codable, Equatable, Sendable {
    public var benchmarkID: String
    public var policyRef: String
    public var checkedAt: Date
    public var screenRecordingPreflight: Bool
    public var accessibilityTrusted: Bool
    public var promptRequested: Bool
    public var captureStarted: Bool
    public var accessibilityObserverStarted: Bool
    public var memoryWriteAllowed: Bool
    public var evidenceRefs: [String]
    public var allowedEffects: [String]
    public var blockedEffects: [String]
    public var safetyNotes: [String]
    public var passed: Bool

    public static func run(
        probe: NativeCapturePermissionProbe = .readCurrentProcess(),
        checkedAt: Date = Date()
    ) -> NativeCapturePermissionSmokeResult {
        let captureStarted = false
        let accessibilityObserverStarted = false
        let memoryWriteAllowed = false
        let evidenceRefs: [String] = []
        let allowedEffects = ["read_permission_status"]
        let blockedEffects = [
            "request_screen_recording_permission",
            "request_accessibility_permission",
            "start_screen_capture",
            "start_accessibility_observer",
            "write_memory",
            "store_raw_evidence",
        ]
        let safetyNotes = [
            "CGPreflightScreenCaptureAccess reads Screen Recording status without prompting.",
            "AXIsProcessTrustedWithOptions uses kAXTrustedCheckOptionPrompt false.",
            "This smoke does not start capture, observers, memory writes, or evidence storage.",
        ]
        let passed = !probe.promptRequested
            && !captureStarted
            && !accessibilityObserverStarted
            && !memoryWriteAllowed
            && evidenceRefs.isEmpty
            && allowedEffects == ["read_permission_status"]
            && blockedEffects.contains("request_screen_recording_permission")
            && blockedEffects.contains("start_screen_capture")

        return NativeCapturePermissionSmokeResult(
            benchmarkID: nativeCapturePermissionSmokeBenchmarkID,
            policyRef: nativeCapturePermissionSmokePolicyRef,
            checkedAt: checkedAt,
            screenRecordingPreflight: probe.screenRecordingPreflight,
            accessibilityTrusted: probe.accessibilityTrusted,
            promptRequested: probe.promptRequested,
            captureStarted: captureStarted,
            accessibilityObserverStarted: accessibilityObserverStarted,
            memoryWriteAllowed: memoryWriteAllowed,
            evidenceRefs: evidenceRefs,
            allowedEffects: allowedEffects,
            blockedEffects: blockedEffects,
            safetyNotes: safetyNotes,
            passed: passed
        )
    }
}

public struct NativeCursorFollowConfig: Codable, Equatable, Sendable {
    public var policyRef: String
    public var sampleHz: Int
    public var overlayDiameter: Double
    public var offsetX: Double
    public var offsetY: Double
    public var displayOnly: Bool
    public var ignoresMouseEvents: Bool
    public var allowedEffects: [String]
    public var blockedEffects: [String]

    public init(
        policyRef: String = nativeCursorFollowPolicyRef,
        sampleHz: Int = 30,
        overlayDiameter: Double = 34,
        offsetX: Double = 14,
        offsetY: Double = -14,
        displayOnly: Bool = true,
        ignoresMouseEvents: Bool = true,
        allowedEffects: [String] = [
            "read_global_cursor_position",
            "render_shadow_clicker_overlay",
            "move_overlay_window",
        ],
        blockedEffects: [String] = [
            "start_screen_capture",
            "start_accessibility_observer",
            "execute_click",
            "type_text",
            "read_window_contents",
            "write_memory",
            "store_raw_evidence",
            "export_payload",
        ]
    ) {
        self.policyRef = policyRef
        self.sampleHz = sampleHz
        self.overlayDiameter = overlayDiameter
        self.offsetX = offsetX
        self.offsetY = offsetY
        self.displayOnly = displayOnly
        self.ignoresMouseEvents = ignoresMouseEvents
        self.allowedEffects = allowedEffects
        self.blockedEffects = blockedEffects
    }

    public func validated() throws -> NativeCursorFollowConfig {
        guard policyRef == nativeCursorFollowPolicyRef else {
            throw ShadowPointerNativeError.invalidControl("native cursor follow policy mismatch")
        }
        guard sampleHz >= 5 && sampleHz <= 60 else {
            throw ShadowPointerNativeError.invalidControl("native cursor follow sampleHz out of range")
        }
        guard overlayDiameter >= 16 && overlayDiameter <= 96 else {
            throw ShadowPointerNativeError.invalidControl("native cursor follow overlay diameter out of range")
        }
        guard displayOnly && ignoresMouseEvents else {
            throw ShadowPointerNativeError.invalidControl("native cursor follow must be display-only")
        }
        let requiredAllowed = Set([
            "read_global_cursor_position",
            "render_shadow_clicker_overlay",
            "move_overlay_window",
        ])
        guard requiredAllowed.isSubset(of: Set(allowedEffects)) else {
            throw ShadowPointerNativeError.invalidControl("native cursor follow missing allowed effects")
        }
        let requiredBlocked = Set([
            "start_screen_capture",
            "start_accessibility_observer",
            "execute_click",
            "type_text",
            "read_window_contents",
            "write_memory",
            "store_raw_evidence",
            "export_payload",
        ])
        guard requiredBlocked.isSubset(of: Set(blockedEffects)) else {
            throw ShadowPointerNativeError.invalidControl("native cursor follow missing blocked effects")
        }
        return self
    }
}

public struct NativeScreenFrameMetadata: Codable, Equatable, Sendable {
    public var width: Int
    public var height: Int

    public init(width: Int, height: Int) {
        self.width = width
        self.height = height
    }
}

public struct NativeScreenCaptureProbeResult: Codable, Equatable, Sendable {
    public var benchmarkID: String
    public var policyRef: String
    public var checkedAt: Date
    public var allowRealCapture: Bool
    public var screenRecordingPreflight: Bool
    public var promptRequested: Bool
    public var captureAttempted: Bool
    public var frameCaptured: Bool
    public var frameWidth: Int?
    public var frameHeight: Int?
    public var skipReason: String?
    public var rawPixelsReturned: Bool
    public var rawRefRetained: Bool
    public var memoryWriteAllowed: Bool
    public var evidenceRefs: [String]
    public var nextUserActions: [String]
    public var allowedEffects: [String]
    public var blockedEffects: [String]
    public var safetyNotes: [String]
    public var passed: Bool

    public static func run(
        allowRealCapture: Bool = false,
        probe: NativeCapturePermissionProbe = .readCurrentProcess(),
        checkedAt: Date = Date(),
        frameProvider: () -> NativeScreenFrameMetadata? = NativeScreenCaptureProbeResult.captureMainDisplayMetadata
    ) -> NativeScreenCaptureProbeResult {
        let captureAttempted = allowRealCapture && probe.screenRecordingPreflight
        let frame = captureAttempted ? frameProvider() : nil
        let frameCaptured = frame != nil
        let skipReason: String?
        let nextUserActions: [String]
        if frameCaptured {
            skipReason = nil
            nextUserActions = []
        } else if !allowRealCapture {
            skipReason = "allow_real_capture_false"
            nextUserActions = [
                "Use the dashboard Screen Probe button or pass --allow-real-capture explicitly."
            ]
        } else if !probe.screenRecordingPreflight {
            skipReason = "screen_recording_preflight_false"
            nextUserActions = [
                "Enable Screen Recording for the hosting app.",
                "Restart the hosting app and run Check Permissions again.",
            ]
        } else {
            skipReason = "frame_metadata_unavailable"
            nextUserActions = ["Run Check Permissions, then retry Screen Probe."]
        }
        let allowedEffects = allowRealCapture
            ? ["read_permission_status", "capture_one_frame_in_memory"]
            : ["read_permission_status"]
        let blockedEffects = [
            "request_screen_recording_permission",
            "start_continuous_screen_capture",
            "return_raw_pixels",
            "store_raw_evidence",
            "write_memory",
            "start_accessibility_observer",
            "click",
            "type_text",
            "export_payload",
        ]
        let safetyNotes = [
            "Real screen capture requires --allow-real-capture and Screen Recording preflight.",
            "The probe captures at most one frame in memory and returns metadata only.",
            "The probe never stores raw pixels, raw refs, evidence refs, or memories.",
        ]
        let passed = !probe.promptRequested
            && (!captureAttempted || frameCaptured)
            && !blockedEffects.isEmpty
            && !allowedEffects.isEmpty

        return NativeScreenCaptureProbeResult(
            benchmarkID: nativeScreenCaptureProbeBenchmarkID,
            policyRef: nativeScreenCaptureProbePolicyRef,
            checkedAt: checkedAt,
            allowRealCapture: allowRealCapture,
            screenRecordingPreflight: probe.screenRecordingPreflight,
            promptRequested: probe.promptRequested,
            captureAttempted: captureAttempted,
            frameCaptured: frameCaptured,
            frameWidth: frame?.width,
            frameHeight: frame?.height,
            skipReason: skipReason,
            rawPixelsReturned: false,
            rawRefRetained: false,
            memoryWriteAllowed: false,
            evidenceRefs: [],
            nextUserActions: nextUserActions,
            allowedEffects: allowedEffects,
            blockedEffects: blockedEffects,
            safetyNotes: safetyNotes,
            passed: passed
        )
    }

    public static func captureMainDisplayMetadata() -> NativeScreenFrameMetadata? {
        #if canImport(CoreGraphics)
        guard let image = CGDisplayCreateImage(CGMainDisplayID()) else {
            return nil
        }
        return NativeScreenFrameMetadata(width: image.width, height: image.height)
        #else
        return nil
        #endif
    }
}

public struct NativeCursorSample: Codable, Equatable, Sendable {
    public var x: Double
    public var y: Double
    public var timestamp: Date

    public init(x: Double, y: Double, timestamp: Date) {
        self.x = x
        self.y = y
        self.timestamp = timestamp
    }
}

public struct NativeCursorFollowSmokeResult: Codable, Equatable, Sendable {
    public var benchmarkID: String
    public var policyRef: String
    public var checkedAt: Date
    public var config: NativeCursorFollowConfig
    public var overlaySpec: NativeOverlayWindowSpec
    public var cursorSamples: [NativeCursorSample]
    public var displayOnly: Bool
    public var captureStarted: Bool
    public var accessibilityObserverStarted: Bool
    public var memoryWriteAllowed: Bool
    public var rawRefRetained: Bool
    public var externalEffects: [String]
    public var passed: Bool

    public static func run(
        samples: [NativeCursorSample] = [
            NativeCursorSample(x: 120, y: 240, timestamp: Date(timeIntervalSince1970: 0)),
            NativeCursorSample(x: 180, y: 260, timestamp: Date(timeIntervalSince1970: 0.1)),
            NativeCursorSample(x: 220, y: 300, timestamp: Date(timeIntervalSince1970: 0.2)),
        ],
        checkedAt: Date = Date()
    ) throws -> NativeCursorFollowSmokeResult {
        let config = try NativeCursorFollowConfig().validated()
        let overlaySpec = NativeOverlayWindowSpec.shadowPointerDefault
        let passed = config.displayOnly
            && config.ignoresMouseEvents
            && overlaySpec.ignoresMouseEventsByDefault
            && !overlaySpec.canBecomeKey
            && !overlaySpec.canBecomeMain
            && samples.count >= 2
        return NativeCursorFollowSmokeResult(
            benchmarkID: nativeCursorFollowBenchmarkID,
            policyRef: nativeCursorFollowPolicyRef,
            checkedAt: checkedAt,
            config: config,
            overlaySpec: overlaySpec,
            cursorSamples: samples,
            displayOnly: true,
            captureStarted: false,
            accessibilityObserverStarted: false,
            memoryWriteAllowed: false,
            rawRefRetained: false,
            externalEffects: [],
            passed: passed
        )
    }
}

public enum NativeCursorProbe {
    public static func sampleNow(timestamp: Date = Date()) -> NativeCursorSample {
        #if canImport(AppKit)
        let point = NSEvent.mouseLocation
        return NativeCursorSample(x: point.x, y: point.y, timestamp: timestamp)
        #else
        return NativeCursorSample(x: 0, y: 0, timestamp: timestamp)
        #endif
    }
}

private func appendUnique(_ values: [String], _ value: String) -> [String] {
    values.contains(value) ? values : values + [value]
}

#if canImport(AppKit)
@available(macOS 13.0, *)
public final class ShadowPointerOverlayPanel: NSPanel {
    public init(contentRect: NSRect) {
        super.init(
            contentRect: contentRect,
            styleMask: [.nonactivatingPanel, .borderless],
            backing: .buffered,
            defer: false
        )
        level = .floating
        collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary, .stationary]
        isOpaque = false
        backgroundColor = .clear
        ignoresMouseEvents = true
        hasShadow = false
        title = "Cortex Shadow Pointer"
        setAccessibilityLabel("Cortex Shadow Pointer")
    }

    public override var canBecomeKey: Bool { false }
    public override var canBecomeMain: Bool { false }
}
#endif

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
public let nativeCursorResponsivenessBenchmarkID = "NATIVE-CURSOR-RESPONSIVENESS-001"
public let nativeOverlayVisualPolishBenchmarkID = "NATIVE-OVERLAY-VISUAL-POLISH-001"
public let nativeOverlayVisualPolishPolicyRef = "policy_native_overlay_visual_polish_v1"
public let nativeAgenticPointerCardBenchmarkID = "NATIVE-AGENTIC-POINTER-CARD-001"
public let nativeAgenticPointerCardPolicyRef = "policy_native_agentic_pointer_card_v1"
public let nativeCompanionHUDPhase2BenchmarkID = "NATIVE-COMPANION-HUD-PHASE2-001"
public let nativeCompanionHUDPhase2PolicyRef = "policy_native_companion_hud_phase2_v1"
public let nativeScreenCaptureProbeBenchmarkID = "NATIVE-SCREEN-CAPTURE-PROBE-001"
public let nativeScreenCaptureProbePolicyRef = "policy_native_screen_capture_probe_v1"
public let nativeInputEffectPolicyRef = "policy_native_input_effects_v1"
public let nativePointerInsightBenchmarkID = "NATIVE-POINTER-INSIGHT-001"
public let nativePointerInsightPolicyRef = "policy_native_pointer_insight_v1"

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

public struct NativeInputEffectPolicy: Codable, Equatable, Sendable {
    public var policyRef: String
    public var nativeInputEffectsEnabled: Bool
    public var requiredLaunchFlag: String
    public var allowedEffectsWhenEnabled: [String]
    public var blockedEffectsWhenDisabled: [String]
    public var requiresExplicitOptIn: Bool

    public init(
        policyRef: String = nativeInputEffectPolicyRef,
        nativeInputEffectsEnabled: Bool = false,
        requiredLaunchFlag: String = "--allow-native-input-effects",
        allowedEffectsWhenEnabled: [String] = [
            "move_system_cursor",
            "click_mouse",
            "right_click_mouse",
            "double_click_mouse",
            "drag_mouse",
            "scroll_mouse",
        ],
        blockedEffectsWhenDisabled: [String] = [
            "move_system_cursor",
            "click_mouse",
            "right_click_mouse",
            "double_click_mouse",
            "drag_mouse",
            "scroll_mouse",
        ],
        requiresExplicitOptIn: Bool = true
    ) {
        self.policyRef = policyRef
        self.nativeInputEffectsEnabled = nativeInputEffectsEnabled
        self.requiredLaunchFlag = requiredLaunchFlag
        self.allowedEffectsWhenEnabled = allowedEffectsWhenEnabled
        self.blockedEffectsWhenDisabled = blockedEffectsWhenDisabled
        self.requiresExplicitOptIn = requiresExplicitOptIn
    }

    public func validated() throws -> NativeInputEffectPolicy {
        guard policyRef == nativeInputEffectPolicyRef else {
            throw ShadowPointerNativeError.invalidControl("native input effect policy mismatch")
        }
        guard requiresExplicitOptIn && requiredLaunchFlag == "--allow-native-input-effects" else {
            throw ShadowPointerNativeError.invalidControl("native input effects must require explicit opt-in")
        }
        let requiredEffects = Set([
            "move_system_cursor",
            "click_mouse",
            "right_click_mouse",
            "double_click_mouse",
            "drag_mouse",
            "scroll_mouse",
        ])
        if nativeInputEffectsEnabled {
            guard requiredEffects.isSubset(of: Set(allowedEffectsWhenEnabled)) else {
                throw ShadowPointerNativeError.invalidControl("enabled native input policy is missing allowed effects")
            }
        } else {
            guard requiredEffects.isSubset(of: Set(blockedEffectsWhenDisabled)) else {
                throw ShadowPointerNativeError.invalidControl("disabled native input policy is missing blocked effects")
            }
        }
        return self
    }
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
    public var cursorHotspotX: Double
    public var cursorHotspotY: Double
    public var displayOnly: Bool
    public var ignoresMouseEvents: Bool
    public var followsSystemWide: Bool
    public var surfaceScope: String
    public var coordinateSpace: String
    public var browserDependency: Bool
    public var maxRenderLatencyMs: Double
    public var maxPointerDriftPx: Double
    public var bubbleAnchorStrategy: String
    public var bubbleMinClearancePx: Double
    public var allowedEffects: [String]
    public var blockedEffects: [String]

    public init(
        policyRef: String = nativeCursorFollowPolicyRef,
        sampleHz: Int = 60,
        overlayDiameter: Double = 34,
        offsetX: Double = 14,
        offsetY: Double = -14,
        cursorHotspotX: Double = 7,
        cursorHotspotY: Double = 58,
        displayOnly: Bool = true,
        ignoresMouseEvents: Bool = true,
        followsSystemWide: Bool = true,
        surfaceScope: String = "system_wide_macos",
        coordinateSpace: String = "global_display_pixels",
        browserDependency: Bool = false,
        maxRenderLatencyMs: Double = 24,
        maxPointerDriftPx: Double = 18,
        bubbleAnchorStrategy: String = "cursor_adjacent_edge_aware",
        bubbleMinClearancePx: Double = 12,
        allowedEffects: [String] = [
            "read_global_cursor_position",
            "render_shadow_clicker_overlay",
            "move_overlay_window",
            "anchor_response_bubble",
        ],
        blockedEffects: [String] = [
            "start_screen_capture",
            "start_accessibility_observer",
            "execute_click",
            "type_text",
            "read_window_contents",
            "move_system_cursor",
            "steal_focus",
            "browser_only_tracking",
            "unanchored_response_bubble",
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
        self.cursorHotspotX = cursorHotspotX
        self.cursorHotspotY = cursorHotspotY
        self.displayOnly = displayOnly
        self.ignoresMouseEvents = ignoresMouseEvents
        self.followsSystemWide = followsSystemWide
        self.surfaceScope = surfaceScope
        self.coordinateSpace = coordinateSpace
        self.browserDependency = browserDependency
        self.maxRenderLatencyMs = maxRenderLatencyMs
        self.maxPointerDriftPx = maxPointerDriftPx
        self.bubbleAnchorStrategy = bubbleAnchorStrategy
        self.bubbleMinClearancePx = bubbleMinClearancePx
        self.allowedEffects = allowedEffects
        self.blockedEffects = blockedEffects
    }

    public func validated() throws -> NativeCursorFollowConfig {
        guard policyRef == nativeCursorFollowPolicyRef else {
            throw ShadowPointerNativeError.invalidControl("native cursor follow policy mismatch")
        }
        guard sampleHz >= 30 && sampleHz <= 120 else {
            throw ShadowPointerNativeError.invalidControl("native cursor follow sampleHz out of range")
        }
        guard overlayDiameter >= 16 && overlayDiameter <= 96 else {
            throw ShadowPointerNativeError.invalidControl("native cursor follow overlay diameter out of range")
        }
        guard cursorHotspotX >= 0 && cursorHotspotY >= 0 else {
            throw ShadowPointerNativeError.invalidControl("native cursor follow hotspot out of range")
        }
        guard displayOnly && ignoresMouseEvents else {
            throw ShadowPointerNativeError.invalidControl("native cursor follow must be display-only")
        }
        guard followsSystemWide
            && surfaceScope == "system_wide_macos"
            && coordinateSpace == "global_display_pixels"
            && !browserDependency
        else {
            throw ShadowPointerNativeError.invalidControl("native cursor follow must be system-wide, not browser-only")
        }
        guard maxRenderLatencyMs > 0 && maxRenderLatencyMs <= 24 else {
            throw ShadowPointerNativeError.invalidControl("native cursor follow latency budget too loose")
        }
        guard maxPointerDriftPx >= 0 && maxPointerDriftPx <= 18 else {
            throw ShadowPointerNativeError.invalidControl("native cursor follow drift budget too loose")
        }
        guard bubbleAnchorStrategy == "cursor_adjacent_edge_aware" && bubbleMinClearancePx >= 8 else {
            throw ShadowPointerNativeError.invalidControl("native response bubble must be cursor-adjacent and edge-aware")
        }
        let requiredAllowed = Set([
            "read_global_cursor_position",
            "render_shadow_clicker_overlay",
            "move_overlay_window",
            "anchor_response_bubble",
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
            "move_system_cursor",
            "steal_focus",
            "browser_only_tracking",
            "unanchored_response_bubble",
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

public struct NativeDisplayFrame: Codable, Equatable, Sendable {
    public var minX: Double
    public var minY: Double
    public var width: Double
    public var height: Double

    public init(minX: Double, minY: Double, width: Double, height: Double) {
        self.minX = minX
        self.minY = minY
        self.width = width
        self.height = height
    }

    public var maxX: Double { minX + width }
    public var maxY: Double { minY + height }

    public static let defaultMain = NativeDisplayFrame(minX: 0, minY: 0, width: 1440, height: 900)

    #if canImport(AppKit)
    public static func containing(_ sample: NativeCursorSample) -> NativeDisplayFrame {
        let point = NSPoint(x: sample.x, y: sample.y)
        let screen = NSScreen.screens.first(where: { $0.frame.contains(point) }) ?? NSScreen.main
        guard let frame = screen?.visibleFrame else {
            return .defaultMain
        }
        return NativeDisplayFrame(
            minX: frame.minX,
            minY: frame.minY,
            width: frame.width,
            height: frame.height
        )
    }
    #endif
}

public struct NativeOverlaySize: Codable, Equatable, Sendable {
    public var width: Double
    public var height: Double

    public init(width: Double, height: Double) {
        self.width = width
        self.height = height
    }

    public static let shadowClickerDefault = NativeOverlaySize(width: 146, height: 68)
}

public struct NativeBubbleSize: Codable, Equatable, Sendable {
    public var width: Double
    public var height: Double

    public init(width: Double, height: Double) {
        self.width = width
        self.height = height
    }

    public static let compactInstruction = NativeBubbleSize(width: 240, height: 72)
}

public struct NativeAgenticPointerCard: Codable, Equatable, Sendable {
    public var benchmarkID: String
    public var policyRef: String
    public var title: String
    public var message: String
    public var status: String
    public var targetLabel: String
    public var routeKind: String
    public var displayOnly: Bool
    public var memoryWriteAllowed: Bool
    public var rawRefRetained: Bool
    public var externalEffectEnabled: Bool
    public var blockedEffects: [String]

    public init(
        benchmarkID: String = nativeAgenticPointerCardBenchmarkID,
        policyRef: String = nativeAgenticPointerCardPolicyRef,
        title: String = "Draft the next steps",
        message: String = "I see Color Page. I can draft the next safe steps.",
        status: String = "draft only | display-only | no write",
        targetLabel: String = "Color Page",
        routeKind: String = "draft_only",
        displayOnly: Bool = true,
        memoryWriteAllowed: Bool = false,
        rawRefRetained: Bool = false,
        externalEffectEnabled: Bool = false,
        blockedEffects: [String] = [
            "start_screen_capture",
            "start_microphone_capture",
            "start_accessibility_observer",
            "move_system_cursor",
            "execute_click",
            "type_text",
            "write_memory_without_review",
            "store_raw_evidence",
            "export_payload",
        ]
    ) {
        self.benchmarkID = benchmarkID
        self.policyRef = policyRef
        self.title = title
        self.message = message
        self.status = status
        self.targetLabel = targetLabel
        self.routeKind = routeKind
        self.displayOnly = displayOnly
        self.memoryWriteAllowed = memoryWriteAllowed
        self.rawRefRetained = rawRefRetained
        self.externalEffectEnabled = externalEffectEnabled
        self.blockedEffects = blockedEffects
    }

    public func validated() throws -> NativeAgenticPointerCard {
        guard benchmarkID == nativeAgenticPointerCardBenchmarkID,
              policyRef == nativeAgenticPointerCardPolicyRef
        else {
            throw ShadowPointerNativeError.invalidControl("native agentic pointer card policy mismatch")
        }
        guard displayOnly && !memoryWriteAllowed && !rawRefRetained && !externalEffectEnabled else {
            throw ShadowPointerNativeError.invalidControl("native agentic pointer card must stay display-only")
        }
        guard title.count <= 44 && message.count <= 82 && status.count <= 54 else {
            throw ShadowPointerNativeError.invalidControl("native agentic pointer copy is too long")
        }
        guard !containsUnsafeMarker([title, message, status, targetLabel, routeKind]) else {
            throw ShadowPointerNativeError.invalidControl("native agentic pointer card contains unsafe marker")
        }
        let requiredBlocked = Set([
            "start_screen_capture",
            "start_microphone_capture",
            "start_accessibility_observer",
            "move_system_cursor",
            "execute_click",
            "type_text",
            "write_memory_without_review",
            "store_raw_evidence",
            "export_payload",
        ])
        guard requiredBlocked.isSubset(of: Set(blockedEffects)) else {
            throw ShadowPointerNativeError.invalidControl("native agentic pointer card missing blocked effects")
        }
        return self
    }

    private func containsUnsafeMarker(_ values: [String]) -> Bool {
        let haystack = values.joined(separator: " ").lowercased()
        return [
            "ignore previous instructions",
            "openai_api_key",
            "sk-",
            "raw://",
            "encrypted_blob://",
            "password",
            "secret",
        ].contains { haystack.contains($0) }
    }
}

public struct NativePointerInsightSnapshot: Codable, Equatable, Sendable {
    public var benchmarkID: String
    public var policyRef: String
    public var mode: String
    public var frontmostApp: String
    public var cursorX: Double
    public var cursorY: Double
    public var displayOnly: Bool
    public var captureStarted: Bool
    public var accessibilityReadStarted: Bool
    public var memoryWriteAllowed: Bool
    public var rawRefRetained: Bool
    public var allowedEffects: [String]
    public var blockedEffects: [String]

    public init(
        benchmarkID: String = nativePointerInsightBenchmarkID,
        policyRef: String = nativePointerInsightPolicyRef,
        mode: String = "hover",
        frontmostApp: String = "current app",
        cursorX: Double,
        cursorY: Double,
        displayOnly: Bool = true,
        captureStarted: Bool = false,
        accessibilityReadStarted: Bool = false,
        memoryWriteAllowed: Bool = false,
        rawRefRetained: Bool = false,
        allowedEffects: [String] = [
            "read_global_cursor_position",
            "read_frontmost_app_name",
            "render_pointer_insight_chip",
        ],
        blockedEffects: [String] = [
            "start_screen_capture",
            "read_window_contents",
            "start_accessibility_observer",
            "execute_click",
            "type_text",
            "write_memory",
            "store_raw_evidence",
            "export_payload",
        ]
    ) {
        self.benchmarkID = benchmarkID
        self.policyRef = policyRef
        self.mode = mode
        self.frontmostApp = frontmostApp
        self.cursorX = cursorX
        self.cursorY = cursorY
        self.displayOnly = displayOnly
        self.captureStarted = captureStarted
        self.accessibilityReadStarted = accessibilityReadStarted
        self.memoryWriteAllowed = memoryWriteAllowed
        self.rawRefRetained = rawRefRetained
        self.allowedEffects = allowedEffects
        self.blockedEffects = blockedEffects
    }

    public func validated(displayFrame: NativeDisplayFrame = .defaultMain) throws -> NativePointerInsightSnapshot {
        guard benchmarkID == nativePointerInsightBenchmarkID,
              policyRef == nativePointerInsightPolicyRef else {
            throw ShadowPointerNativeError.invalidControl("native pointer insight policy mismatch")
        }
        guard ["hover", "selection"].contains(mode) else {
            throw ShadowPointerNativeError.invalidControl("native pointer insight mode is unsupported")
        }
        guard cursorX >= displayFrame.minX,
              cursorX <= displayFrame.maxX,
              cursorY >= displayFrame.minY,
              cursorY <= displayFrame.maxY else {
            throw ShadowPointerNativeError.invalidControl("native pointer insight cursor outside display bounds")
        }
        guard displayOnly,
              !captureStarted,
              !accessibilityReadStarted,
              !memoryWriteAllowed,
              !rawRefRetained else {
            throw ShadowPointerNativeError.invalidControl("native pointer insight must stay display-only")
        }
        let requiredBlocked = Set([
            "start_screen_capture",
            "read_window_contents",
            "start_accessibility_observer",
            "execute_click",
            "type_text",
            "write_memory",
            "store_raw_evidence",
            "export_payload",
        ])
        guard requiredBlocked.isSubset(of: Set(blockedEffects)) else {
            throw ShadowPointerNativeError.invalidControl("native pointer insight missing blocked effects")
        }
        return self
    }

    public var chipText: String {
        let safeApp = frontmostApp.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
            ? "this app"
            : frontmostApp
        if mode == "selection" {
            return "Pinned this spot in \(safeApp). Hold Control and ask what to do next."
        }
        return "Looking at \(safeApp) near your pointer. Hold Control and ask about this."
    }

    public var contextText: String {
        let safeApp = frontmostApp.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
            ? "current app"
            : frontmostApp
        return "Frontmost app \(safeApp). Pointer at x \(Int(cursorX)), y \(Int(cursorY)). No screen capture, raw pixels, or window text were read."
    }
}

public struct NativeOverlayVisualSpec: Codable, Equatable, Sendable {
    public var benchmarkID: String
    public var policyRef: String
    public var visualStyle: String
    public var material: String
    public var vibrancyEnabled: Bool
    public var tintSemanticOnly: Bool
    public var cursorShape: String
    public var cursorStrokeColor: String
    public var cursorFillColor: String
    public var cursorHotspotVisible: Bool
    public var bubbleCornerRadius: Double
    public var bubbleShadowRadius: Double
    public var bubbleMaxWidth: Double
    public var loadingAnimation: String
    public var loadingDotCount: Int
    public var loadingFrameRateHz: Int
    public var motionCurve: String
    public var animationRespectsReducedMotion: Bool
    public var maxTextLines: Int
    public var foregroundStyle: String
    public var avoidsOpaqueScrim: Bool
    public var glassElementsGrouped: Bool
    public var displayOnly: Bool
    public var blockedEffects: [String]

    public init(
        benchmarkID: String = nativeOverlayVisualPolishBenchmarkID,
        policyRef: String = nativeOverlayVisualPolishPolicyRef,
        visualStyle: String = "apple_liquid_glass_companion",
        material: String = "hud_window_vibrant_material",
        vibrancyEnabled: Bool = true,
        tintSemanticOnly: Bool = true,
        cursorShape: String = "system_mouse_cloak",
        cursorStrokeColor: String = "system_blue",
        cursorFillColor: String = "translucent_blue_cloak",
        cursorHotspotVisible: Bool = true,
        bubbleCornerRadius: Double = 18,
        bubbleShadowRadius: Double = 24,
        bubbleMaxWidth: Double = 260,
        loadingAnimation: String = "three_dot_breathing",
        loadingDotCount: Int = 3,
        loadingFrameRateHz: Int = 30,
        motionCurve: String = "low_latency_linear_follow_soft_opacity",
        animationRespectsReducedMotion: Bool = true,
        maxTextLines: Int = 2,
        foregroundStyle: String = "vibrant_label_and_secondary_label",
        avoidsOpaqueScrim: Bool = true,
        glassElementsGrouped: Bool = true,
        displayOnly: Bool = true,
        blockedEffects: [String] = [
            "start_screen_capture",
            "start_accessibility_observer",
            "execute_click",
            "type_text",
            "move_system_cursor",
            "steal_focus",
            "write_memory",
            "store_raw_evidence",
            "export_payload",
        ]
    ) {
        self.benchmarkID = benchmarkID
        self.policyRef = policyRef
        self.visualStyle = visualStyle
        self.material = material
        self.vibrancyEnabled = vibrancyEnabled
        self.tintSemanticOnly = tintSemanticOnly
        self.cursorShape = cursorShape
        self.cursorStrokeColor = cursorStrokeColor
        self.cursorFillColor = cursorFillColor
        self.cursorHotspotVisible = cursorHotspotVisible
        self.bubbleCornerRadius = bubbleCornerRadius
        self.bubbleShadowRadius = bubbleShadowRadius
        self.bubbleMaxWidth = bubbleMaxWidth
        self.loadingAnimation = loadingAnimation
        self.loadingDotCount = loadingDotCount
        self.loadingFrameRateHz = loadingFrameRateHz
        self.motionCurve = motionCurve
        self.animationRespectsReducedMotion = animationRespectsReducedMotion
        self.maxTextLines = maxTextLines
        self.foregroundStyle = foregroundStyle
        self.avoidsOpaqueScrim = avoidsOpaqueScrim
        self.glassElementsGrouped = glassElementsGrouped
        self.displayOnly = displayOnly
        self.blockedEffects = blockedEffects
    }

    public func validated() throws -> NativeOverlayVisualSpec {
        guard benchmarkID == nativeOverlayVisualPolishBenchmarkID else {
            throw ShadowPointerNativeError.invalidControl("native overlay visual benchmark mismatch")
        }
        guard policyRef == nativeOverlayVisualPolishPolicyRef else {
            throw ShadowPointerNativeError.invalidControl("native overlay visual policy mismatch")
        }
        guard visualStyle == "apple_liquid_glass_companion" else {
            throw ShadowPointerNativeError.invalidControl("native overlay visual style mismatch")
        }
        guard material == "hud_window_vibrant_material" && vibrancyEnabled else {
            throw ShadowPointerNativeError.invalidControl("native overlay must use system material and vibrancy")
        }
        guard tintSemanticOnly && avoidsOpaqueScrim && glassElementsGrouped else {
            throw ShadowPointerNativeError.invalidControl("native overlay glass treatment is too custom or heavy")
        }
        guard cursorShape == "system_mouse_cloak" && cursorHotspotVisible else {
            throw ShadowPointerNativeError.invalidControl("native overlay cursor affordance is unclear")
        }
        guard bubbleCornerRadius >= 14 && bubbleCornerRadius <= 24 else {
            throw ShadowPointerNativeError.invalidControl("native overlay bubble radius outside desktop glass range")
        }
        guard loadingAnimation == "three_dot_breathing"
            && loadingDotCount == 3
            && loadingFrameRateHz >= 24
            && animationRespectsReducedMotion
        else {
            throw ShadowPointerNativeError.invalidControl("native overlay loading animation is not product-ready")
        }
        guard maxTextLines <= 2 && foregroundStyle == "vibrant_label_and_secondary_label" else {
            throw ShadowPointerNativeError.invalidControl("native overlay text treatment is too dense")
        }
        guard displayOnly else {
            throw ShadowPointerNativeError.invalidControl("native overlay visual layer must be display-only")
        }
        let requiredBlocked = Set([
            "start_screen_capture",
            "start_accessibility_observer",
            "execute_click",
            "type_text",
            "move_system_cursor",
            "steal_focus",
            "write_memory",
            "store_raw_evidence",
            "export_payload",
        ])
        guard requiredBlocked.isSubset(of: Set(blockedEffects)) else {
            throw ShadowPointerNativeError.invalidControl("native overlay visual spec missing blocked effects")
        }
        return self
    }
}

public struct NativeOverlayPlacement: Codable, Equatable, Sendable {
    public var overlayOriginX: Double
    public var overlayOriginY: Double
    public var visualCursorX: Double
    public var visualCursorY: Double
    public var desiredCursorX: Double
    public var desiredCursorY: Double
    public var pointerDriftPx: Double
    public var bubbleX: Double
    public var bubbleY: Double
    public var bubbleSide: String
    public var bubbleAnchoredTo: String
    public var displayFrame: NativeDisplayFrame
}

public struct NativeChipPlacement: Codable, Equatable, Sendable {
    public var x: Double
    public var y: Double
    public var width: Double
    public var height: Double
    public var side: String

    public var maxX: Double { x + width }
    public var maxY: Double { y + height }
}

public enum NativeChipPlacementEngine {
    public static func place(
        cursorX: Double,
        cursorY: Double,
        chipWidth: Double,
        chipHeight: Double,
        visibleFrame: NativeDisplayFrame,
        gap: Double = 20,
        margin: Double = 10
    ) -> NativeChipPlacement {
        let safeGap = max(8, gap)
        let safeMargin = max(0, margin)
        let safeWidth = min(max(1, chipWidth), max(1, visibleFrame.width - safeMargin * 2))
        let safeHeight = min(max(1, chipHeight), max(1, visibleFrame.height - safeMargin * 2))
        let fitsRight = cursorX + safeGap + safeWidth <= visibleFrame.maxX - safeMargin
        let rawX = fitsRight ? cursorX + safeGap : cursorX - safeGap - safeWidth
        let rawY = cursorY - safeHeight / 2
        return NativeChipPlacement(
            x: clamp(rawX, visibleFrame.minX + safeMargin, visibleFrame.maxX - safeWidth - safeMargin),
            y: clamp(rawY, visibleFrame.minY + safeMargin, visibleFrame.maxY - safeHeight - safeMargin),
            width: safeWidth,
            height: safeHeight,
            side: fitsRight ? "right" : "left"
        )
    }

    private static func clamp(_ value: Double, _ lower: Double, _ upper: Double) -> Double {
        min(max(value, lower), upper)
    }
}

public struct NativeAnimationTimingSpec: Codable, Equatable, Sendable {
    public var benchmarkID: String
    public var policyRef: String
    public var displayDriver: String
    public var targetRefreshHz: Int
    public var easingCurve: String
    public var transitionDurationMs: Int
    public var amplitudeReactiveRing: Bool
    public var connectionErrorIndicator: String

    public init(
        benchmarkID: String = nativeCompanionHUDPhase2BenchmarkID,
        policyRef: String = nativeCompanionHUDPhase2PolicyRef,
        displayDriver: String = "CVDisplayLink",
        targetRefreshHz: Int = 120,
        easingCurve: String = "cubic_ease_in_out",
        transitionDurationMs: Int = 220,
        amplitudeReactiveRing: Bool = true,
        connectionErrorIndicator: String = "warm_amber_glass_chip"
    ) {
        self.benchmarkID = benchmarkID
        self.policyRef = policyRef
        self.displayDriver = displayDriver
        self.targetRefreshHz = targetRefreshHz
        self.easingCurve = easingCurve
        self.transitionDurationMs = transitionDurationMs
        self.amplitudeReactiveRing = amplitudeReactiveRing
        self.connectionErrorIndicator = connectionErrorIndicator
    }

    public func validated() throws -> NativeAnimationTimingSpec {
        guard benchmarkID == nativeCompanionHUDPhase2BenchmarkID,
              policyRef == nativeCompanionHUDPhase2PolicyRef
        else {
            throw ShadowPointerNativeError.invalidControl("native companion HUD phase 2 policy mismatch")
        }
        guard displayDriver == "CVDisplayLink" && targetRefreshHz >= 60 && targetRefreshHz <= 120 else {
            throw ShadowPointerNativeError.invalidControl("native companion HUD requires display-synced refresh")
        }
        guard easingCurve == "cubic_ease_in_out" && transitionDurationMs >= 120 && transitionDurationMs <= 320 else {
            throw ShadowPointerNativeError.invalidControl("native companion HUD transition curve mismatch")
        }
        guard amplitudeReactiveRing && connectionErrorIndicator == "warm_amber_glass_chip" else {
            throw ShadowPointerNativeError.invalidControl("native companion HUD missing phase 2 visual affordances")
        }
        return self
    }
}

public enum NativeCursorPlacementEngine {
    public static func place(
        sample: NativeCursorSample,
        config: NativeCursorFollowConfig = NativeCursorFollowConfig(),
        displayFrame: NativeDisplayFrame = .defaultMain,
        overlaySize: NativeOverlaySize = .shadowClickerDefault,
        bubbleSize: NativeBubbleSize = .compactInstruction
    ) throws -> NativeOverlayPlacement {
        let config = try config.validated()
        let desiredCursorX = sample.x + config.offsetX
        let desiredCursorY = sample.y + config.offsetY
        let rawOriginX = desiredCursorX - config.cursorHotspotX
        let rawOriginY = desiredCursorY - config.cursorHotspotY
        let overlayOriginX = clamp(rawOriginX, displayFrame.minX, displayFrame.maxX - overlaySize.width)
        let overlayOriginY = clamp(rawOriginY, displayFrame.minY, displayFrame.maxY - overlaySize.height)
        let visualCursorX = overlayOriginX + config.cursorHotspotX
        let visualCursorY = overlayOriginY + config.cursorHotspotY
        let drift = hypot(visualCursorX - desiredCursorX, visualCursorY - desiredCursorY)

        let gap = max(config.bubbleMinClearancePx, 8)
        let bubbleFitsRight = desiredCursorX + gap + bubbleSize.width <= displayFrame.maxX
        let bubbleX = bubbleFitsRight
            ? desiredCursorX + gap
            : desiredCursorX - gap - bubbleSize.width
        let bubbleY = clamp(
            desiredCursorY - bubbleSize.height / 2,
            displayFrame.minY + gap,
            displayFrame.maxY - bubbleSize.height - gap
        )

        return NativeOverlayPlacement(
            overlayOriginX: bubbleFitsRight
                ? overlayOriginX
                : clamp(overlayOriginX, displayFrame.minX, displayFrame.maxX - overlaySize.width),
            overlayOriginY: overlayOriginY,
            visualCursorX: visualCursorX,
            visualCursorY: visualCursorY,
            desiredCursorX: desiredCursorX,
            desiredCursorY: desiredCursorY,
            pointerDriftPx: drift,
            bubbleX: clamp(bubbleX, displayFrame.minX + gap, displayFrame.maxX - bubbleSize.width - gap),
            bubbleY: bubbleY,
            bubbleSide: bubbleFitsRight ? "right" : "left",
            bubbleAnchoredTo: "system_cursor",
            displayFrame: displayFrame
        )
    }

    private static func clamp(_ value: Double, _ lower: Double, _ upper: Double) -> Double {
        min(max(value, lower), upper)
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
    public var visualSpec: NativeOverlayVisualSpec
    public var cursorSamples: [NativeCursorSample]
    public var displayOnly: Bool
    public var captureStarted: Bool
    public var accessibilityObserverStarted: Bool
    public var memoryWriteAllowed: Bool
    public var rawRefRetained: Bool
    public var externalEffects: [String]
    public var placementSamples: [NativeOverlayPlacement]
    public var sampleIntervalMs: Double
    public var maxRenderLatencyMsAllowed: Double
    public var maxPointerDriftPxMeasured: Double
    public var systemWideReady: Bool
    public var bubbleAnchorReady: Bool
    public var browserDependency: Bool
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
        let visualSpec = try NativeOverlayVisualSpec().validated()
        let placementSamples = try samples.map {
            try NativeCursorPlacementEngine.place(sample: $0, config: config)
        }
        let maxDrift = placementSamples.map(\.pointerDriftPx).max() ?? 0
        let systemWideReady = config.followsSystemWide
            && config.surfaceScope == "system_wide_macos"
            && config.coordinateSpace == "global_display_pixels"
            && !config.browserDependency
        let bubbleAnchorReady = placementSamples.allSatisfy {
            $0.bubbleAnchoredTo == "system_cursor"
                && $0.bubbleX >= $0.displayFrame.minX
                && $0.bubbleY >= $0.displayFrame.minY
                && $0.bubbleX <= $0.displayFrame.maxX
                && $0.bubbleY <= $0.displayFrame.maxY
        }
        let passed = config.displayOnly
            && config.ignoresMouseEvents
            && overlaySpec.ignoresMouseEventsByDefault
            && !overlaySpec.canBecomeKey
            && !overlaySpec.canBecomeMain
            && samples.count >= 2
            && systemWideReady
            && bubbleAnchorReady
            && maxDrift <= config.maxPointerDriftPx
            && visualSpec.displayOnly
            && visualSpec.material == "hud_window_vibrant_material"
            && visualSpec.loadingAnimation == "three_dot_breathing"
        return NativeCursorFollowSmokeResult(
            benchmarkID: nativeCursorFollowBenchmarkID,
            policyRef: nativeCursorFollowPolicyRef,
            checkedAt: checkedAt,
            config: config,
            overlaySpec: overlaySpec,
            visualSpec: visualSpec,
            cursorSamples: samples,
            displayOnly: true,
            captureStarted: false,
            accessibilityObserverStarted: false,
            memoryWriteAllowed: false,
            rawRefRetained: false,
            externalEffects: [],
            placementSamples: placementSamples,
            sampleIntervalMs: 1000.0 / Double(config.sampleHz),
            maxRenderLatencyMsAllowed: config.maxRenderLatencyMs,
            maxPointerDriftPxMeasured: maxDrift,
            systemWideReady: systemWideReady,
            bubbleAnchorReady: bubbleAnchorReady,
            browserDependency: config.browserDependency,
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

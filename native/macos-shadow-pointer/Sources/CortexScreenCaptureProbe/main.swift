import CortexShadowPointerNative
import Foundation

struct ScreenCaptureProbeArgs {
    var json = false
    var allowRealCapture = false

    init(_ arguments: [String]) throws {
        var iterator = arguments.dropFirst().makeIterator()
        while let argument = iterator.next() {
            switch argument {
            case "--json":
                json = true
            case "--allow-real-capture":
                allowRealCapture = true
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
    let args = try ScreenCaptureProbeArgs(CommandLine.arguments)
    let result = NativeScreenCaptureProbeResult.run(allowRealCapture: args.allowRealCapture)
    if args.json {
        print(String(decoding: try encoder.encode(result), as: UTF8.self))
    } else {
        print(
            "\(nativeScreenCaptureProbeBenchmarkID): passed=\(result.passed) "
                + "attempted=\(result.captureAttempted) captured=\(result.frameCaptured)"
        )
    }
    if !result.passed {
        exit(1)
    }
} catch {
    fputs("Cortex screen capture probe failed: \(error)\n", stderr)
    exit(1)
}

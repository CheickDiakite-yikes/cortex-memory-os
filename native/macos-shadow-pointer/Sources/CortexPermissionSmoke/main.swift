import CortexShadowPointerNative
import Foundation

let result = NativeCapturePermissionSmokeResult.run()
let encoder = JSONEncoder()
encoder.dateEncodingStrategy = .iso8601
encoder.keyEncodingStrategy = .convertToSnakeCase
encoder.outputFormatting = [.prettyPrinted, .sortedKeys]

do {
    let data = try encoder.encode(result)
    print(String(decoding: data, as: UTF8.self))
    if !result.passed {
        exit(1)
    }
} catch {
    fputs("Cortex native permission smoke failed: \(error)\n", stderr)
    exit(1)
}

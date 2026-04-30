// swift-tools-version: 6.0

import PackageDescription

let package = Package(
    name: "CortexShadowPointerNative",
    platforms: [
        .macOS(.v13)
    ],
    products: [
        .library(
            name: "CortexShadowPointerNative",
            targets: ["CortexShadowPointerNative"]
        ),
        .executable(
            name: "cortex-shadow-pointer-smoke",
            targets: ["CortexShadowPointerSmoke"]
        ),
        .executable(
            name: "cortex-permission-smoke",
            targets: ["CortexPermissionSmoke"]
        ),
    ],
    targets: [
        .target(
            name: "CortexShadowPointerNative"
        ),
        .executableTarget(
            name: "CortexShadowPointerSmoke",
            dependencies: ["CortexShadowPointerNative"]
        ),
        .executableTarget(
            name: "CortexPermissionSmoke",
            dependencies: ["CortexShadowPointerNative"]
        ),
        .testTarget(
            name: "CortexShadowPointerNativeTests",
            dependencies: ["CortexShadowPointerNative"]
        ),
    ]
)

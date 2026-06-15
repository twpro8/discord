import { defineConfig, type UserConfig } from "@hey-api/openapi-ts";

const config: Promise<UserConfig> = defineConfig({
    input: "./openapi.json",
    logs: {
        path: "./logs",
    },
    output: "./src/client",
    plugins: [
        "@hey-api/client-fetch",
        "@hey-api/schemas",
        {
            name: "@hey-api/sdk",
            operations: {
                strategy: "byTags",
                containerName: (name: string) => {
                    const singular = name.endsWith("s") ? name.slice(0, -1) : name;
                    return `${singular}Service`;
                },
                nesting: "operationId",
                methodName: (name: string) => {
                    const withoutService = name.includes("-") ? name.split("-")[1] : name;
                    return withoutService.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
                },
            },
        },
        {
            enums: "javascript",
            name: "@hey-api/typescript",
        },
        "@tanstack/react-query",
    ],
});

export default config;

/** @type {import("prettier").Config} */
export default {
  plugins: ['@ianvs/prettier-plugin-sort-imports'],
  importOrder: [
    "^react",
    "",
    "<THIRD_PARTY_MODULES>",
    "",
    "^@/shared/",
    "",
    "^@/entities/",
    "",
    "^@/(features|pages)/",
    "",
    "^[./]",
  ],
  importOrderTypeScriptVersion: "6.0.0",
  importOrderCaseSensitive: false,
}

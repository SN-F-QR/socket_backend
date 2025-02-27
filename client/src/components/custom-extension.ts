import Heading from "@tiptap/extension-heading";

export interface CustomExtensionOptions {
  levels: number[];
}

export const CustomHeading = Heading.extend<CustomExtensionOptions>({
  addOptions() {
    return {
      levels: [1],
    };
  },
  addAttributes() {
    return {
      ...this.parent?.(),
      id: {
        default: "114514",
      },
    };
  },
});

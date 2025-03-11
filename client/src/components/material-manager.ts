import data from "../../study-setting.json";

export type Material = {
  city: string;
  pdf: string;
  video: string;
  transcript: string;
};

export const materials: Material[] = data as Material[];

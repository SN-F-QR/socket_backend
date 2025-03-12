export const baseStyles = "transition duration-300 rounded-md";

export const colors = {
  normal: "bg-sky-500",
  spark: "bg-gradient-to-r from-sky-500 to-indigo-500",
  danger: "bg-red-500",
};

export const getButtonStyles = (): string => {
  return `${baseStyles} ${colors.normal} flex min-w-36 justify-center space-x-1 px-4 py-2 text-white hover:bg-sky-600 hover:shadow-lg shadow-md hover:scale-[1.05]`;
};

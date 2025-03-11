export const getButtonStyles = (): string => {
  const baseStyles = "transition duration-300 rounded-md bg-sky-500";

  return `${baseStyles} flex min-w-28 justify-center space-x-1 px-4 py-2 text-white hover:bg-sky-600 hover:shadow-lg shadow-md hover:scale-[1.05]`;
};

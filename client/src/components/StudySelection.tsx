import { getButtonStyles } from "./button";
import { Material } from "./material-manager";

type StudySelectionProps = {
  materials: Material[];
  setMaterial: (value: Material) => void;
};

const StudySelection = (props: StudySelectionProps) => {
  const selectionList = props.materials.map((material) => {
    return (
      <button
        key={material.city}
        className={`${getButtonStyles()} cursor-default text-lg`}
        onClick={() => {
          props.setMaterial(material);
        }}
      >
        {material.city}
      </button>
    );
  });

  return (
    <div className="flex h-full flex-col items-center justify-center space-y-3">
      <h1 className="place-self-center text-nowrap text-xl">
        Choose your travel city
      </h1>
      {selectionList}
    </div>
  );
};

export default StudySelection;

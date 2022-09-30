type Dict = { [key: string]: string | any[] | Dict };

const data: Dict = {
  a: "a",
  b: {
    c: "c",
    d: {
      b: {
        a: "a",
      },
    },
  },
  c: ["awa"],
};
const output: Record<string, string | any[]> = {};

const get_get = (key: string[], value: string | any[] | Dict) => {
  if (typeof value === "string" || Array.isArray(value)) {
    output[key.join(".")] = value;
  } else {
    for (const [k, data] of Object.entries(value)) get_get([...key, k], data);
  }
};
get_get([], data);
console.log(output);

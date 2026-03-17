const instances = /* @__PURE__ */ new WeakMap();
const MyComponent = (args) => {
  const { parentElement, data, setStateValue } = args;
  const rootElement = parentElement.querySelector(".component-root");
  if (!rootElement) {
    throw new Error("Unexpected: root element not found");
  }
  const heading = rootElement.querySelector("h1");
  if (heading) {
    heading.textContent = `Hello, ${data.name}!`;
  }
  const button = rootElement.querySelector("button");
  if (!button) {
    throw new Error("Unexpected: button element not found");
  }
  const handleClick = () => {
    const numClicks = (instances.get(parentElement)?.numClicks || 0) + 1;
    instances.set(parentElement, { numClicks });
    setStateValue("num_clicks", numClicks);
  };
  if (!instances.has(parentElement)) {
    button.addEventListener("click", handleClick);
    instances.set(parentElement, { numClicks: 0 });
  }
  return () => {
    button.removeEventListener("click", handleClick);
    instances.delete(parentElement);
  };
};
export {
  MyComponent as default
};
//# sourceMappingURL=index-ClAl6rwu.js.map

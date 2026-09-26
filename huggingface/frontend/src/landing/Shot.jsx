export default function Shot({ name, alt, priority = false, className = "" }) {
  const shared = {
    width: 1440,
    height: 900,
    decoding: "async",
    loading: priority ? "eager" : "lazy",
    fetchPriority: priority ? "high" : "auto",
  };

  return (
    <>
      <img src={`/shots/${name}-light.png`} alt={alt} className={`dark:hidden ${className}`} {...shared} />
      <img src={`/shots/${name}-dark.png`} alt="" aria-hidden="true" className={`hidden dark:block ${className}`} {...shared} />
    </>
  );
}

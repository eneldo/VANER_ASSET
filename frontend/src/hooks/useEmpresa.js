export default function useEmpresa() {
  const user = JSON.parse(
    localStorage.getItem("user")
  );

  return user?.empresa_id;
}

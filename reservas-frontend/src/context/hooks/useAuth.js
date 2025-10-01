import { useContext } from "react";
import { AuthContext } from "../AuthContext";

// Hook de acceso
export const useAuth = () => useContext(AuthContext);
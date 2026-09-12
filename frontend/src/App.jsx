import { useEffect, useState } from "react";
import { checkHealth } from "./services/api";

export default function App() {
  const [backendStatus, setBackendStatus] = useState("checking");

  useEffect(() => {
    async function testBackend() {
      try {
        await checkHealth();
        setBackendStatus("connected");
      } catch (error) {
        setBackendStatus("error");
      }
    }

    testBackend();
  }, []);

  return (
    <main className="shell">
      <section className="hero">
        <p className="eyebrow">GUARDIAN · FRAUD RISK MONITOR</p>

        <h1>Detección de fraude financiero en tiempo real</h1>

        <p className="subtitle">
          MVP del hackathon. El dashboard se conectará al motor de riesgo y a Nessie.
        </p>

        <div className={`status ${backendStatus}`}>
          <span />
          {backendStatus === "checking" && "Comprobando backend..."}
          {backendStatus === "connected" && "Backend conectado"}
          {backendStatus === "error" && "Backend desconectado"}
        </div>
      </section>
    </main>
  );
}

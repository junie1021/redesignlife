import { useState } from "react";
import type { TypeKey, ViewKey } from "../types";
import { Nav } from "../components/Nav";
import { Section1 } from "../components/Section1";
import { Section2 } from "../components/Section2";
import { Section3 } from "../components/Section3";

export default function App() {
  const [view, setView] = useState<ViewKey>("s1");
  const [userType, setUserType] = useState<TypeKey | null>(null);

  const resolvedType: TypeKey = userType ?? "perfectionist";

  return (

    <div 
    
      className="min-h-screen bg-background"
      style={{ fontFamily: "'Noto Sans KR', -apple-system, sans-serif" }}
    >

      <Nav view={view} onNavigate={setView} />

      {view === "s1" && (
        <Section1
          typeKey={userType}
          onSetType={setUserType}
          onNext={() => setView("s2")}
        />
      )}

      {view === "s2" && (
        <Section2
          key={resolvedType}
          typeKey={resolvedType}
          onNext={() => setView("s3")}
        />
      )}

      {view === "s3" && (
        <Section3
          key={resolvedType}
          typeKey={resolvedType}
          onRestart={() => setView("s1")}
        />
      )}
    </div>
  );
}

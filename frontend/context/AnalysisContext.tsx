"use client";

import React, {
  createContext,
  useContext,
  useReducer,
  useCallback,
  ReactNode,
} from "react";
import {
  AnalysisConfig,
  AnalysisResult,
  AnalysisStatus,
  PolygonData,
} from "@/lib/types";
import { api } from "@/lib/api";

export interface AnalysisState {
  polygon: PolygonData | null;
  areaHa: number | null;
  analysisStatus: AnalysisStatus;
  results: AnalysisResult | null;
  progressStep: number;
  analysisConfig: AnalysisConfig;
  error: string | null;
}

export type AnalysisAction =
  | { type: "SET_POLYGON"; payload: PolygonData | null }
  | { type: "CLEAR_POLYGON" }
  | { type: "SET_AREA"; payload: number | null }
  | { type: "SET_STATUS"; payload: AnalysisStatus }
  | { type: "SET_RESULTS"; payload: AnalysisResult | null }
  | { type: "SET_PROGRESS_STEP"; payload: number }
  | { type: "SET_CONFIG"; payload: Partial<AnalysisConfig> }
  | { type: "SET_ERROR"; payload: string | null }
  | { type: "RESET_ANALYSIS" };

const initialConfig: AnalysisConfig = {
  data_sources: [
    "Sentinel-2 MSI (10m)",
    "GEDI L2B Canopy Height",
    "ALOS PALSAR-2 SAR",
  ],
  analysis_type: "detailed",
  drone_image: null,
};

const initialState: AnalysisState = {
  polygon: null,
  areaHa: null,
  analysisStatus: "idle",
  results: null,
  progressStep: 0,
  analysisConfig: initialConfig,
  error: null,
};

function analysisReducer(
  state: AnalysisState,
  action: AnalysisAction
): AnalysisState {
  switch (action.type) {
    case "SET_POLYGON":
      return {
        ...state,
        polygon: action.payload,
      };
    case "CLEAR_POLYGON":
      return {
        ...state,
        polygon: null,
        areaHa: null,
        results: null,
        analysisStatus: "idle",
        progressStep: 0,
        error: null,
      };
    case "SET_AREA":
      return {
        ...state,
        areaHa: action.payload,
      };
    case "SET_STATUS":
      return {
        ...state,
        analysisStatus: action.payload,
      };
    case "SET_RESULTS":
      return {
        ...state,
        results: action.payload,
      };
    case "SET_PROGRESS_STEP":
      return {
        ...state,
        progressStep: action.payload,
      };
    case "SET_CONFIG":
      return {
        ...state,
        analysisConfig: {
          ...state.analysisConfig,
          ...action.payload,
        },
      };
    case "SET_ERROR":
      return {
        ...state,
        error: action.payload,
      };
    case "RESET_ANALYSIS":
      return {
        ...initialState,
      };
    default:
      return state;
  }
}

export interface AnalysisContextType {
  state: AnalysisState;
  dispatch: React.Dispatch<AnalysisAction>;
  runAnalysis: () => Promise<void>;
  setPolygon: (polygon: PolygonData | null) => void;
  clearPolygon: () => void;
  setArea: (area: number | null) => void;
  setStatus: (status: AnalysisStatus) => void;
  setResults: (results: AnalysisResult | null) => void;
  setProgressStep: (step: number) => void;
  setConfig: (config: Partial<AnalysisConfig>) => void;
  setError: (error: string | null) => void;
  resetAnalysis: () => void;
}

const AnalysisContext = createContext<AnalysisContextType | undefined>(
  undefined
);

export function AnalysisProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(analysisReducer, initialState);

  const setPolygon = useCallback((polygon: PolygonData | null) => {
    dispatch({ type: "SET_POLYGON", payload: polygon });
  }, []);

  const clearPolygon = useCallback(() => {
    dispatch({ type: "CLEAR_POLYGON" });
  }, []);

  const setArea = useCallback((area: number | null) => {
    dispatch({ type: "SET_AREA", payload: area });
  }, []);

  const setStatus = useCallback((status: AnalysisStatus) => {
    dispatch({ type: "SET_STATUS", payload: status });
  }, []);

  const setResults = useCallback((results: AnalysisResult | null) => {
    dispatch({ type: "SET_RESULTS", payload: results });
  }, []);

  const setProgressStep = useCallback((step: number) => {
    dispatch({ type: "SET_PROGRESS_STEP", payload: step });
  }, []);

  const setConfig = useCallback((config: Partial<AnalysisConfig>) => {
    dispatch({ type: "SET_CONFIG", payload: config });
  }, []);

  const setError = useCallback((error: string | null) => {
    dispatch({ type: "SET_ERROR", payload: error });
  }, []);

  const resetAnalysis = useCallback(() => {
    dispatch({ type: "RESET_ANALYSIS" });
  }, []);

  const runAnalysis = useCallback(async () => {
    if (!state.polygon) {
      dispatch({
        type: "SET_ERROR",
        payload: "Please select or draw a forest area on the map before running analysis.",
      });
      dispatch({ type: "SET_STATUS", payload: "error" });
      return;
    }

    if (state.areaHa && state.areaHa < 10.0) {
      dispatch({
        type: "SET_ERROR",
        payload: `The selected area (${state.areaHa} ha) is below the minimum required boundary threshold of 10.0 hectares for satellite estimation. Please draw or select a larger boundary.`,
      });
      dispatch({ type: "SET_STATUS", payload: "error" });
      return;
    }

    dispatch({ type: "SET_STATUS", payload: "loading" });
    dispatch({ type: "SET_ERROR", payload: null });
    dispatch({ type: "SET_PROGRESS_STEP", payload: 1 });

    let progressTimer: NodeJS.Timeout | null = null;

    try {
      // Step interval timer to animate visual progress
      progressTimer = setInterval(() => {
        dispatch({
          type: "SET_PROGRESS_STEP",
          payload: Math.min(4, Math.floor(Date.now() / 1500) % 4 + 1),
        });
      }, 1200);

      // Call real backend API for live computation
      const realResult = await api.analyze(
        state.polygon,
        state.analysisConfig.data_sources,
        state.analysisConfig.analysis_type
      );

      if (progressTimer) clearInterval(progressTimer);

      dispatch({ type: "SET_PROGRESS_STEP", payload: 5 });
      await new Promise((resolve) => setTimeout(resolve, 800));

      dispatch({ type: "SET_RESULTS", payload: realResult });
      dispatch({ type: "SET_STATUS", payload: "complete" });
    } catch (err) {
      if (progressTimer) clearInterval(progressTimer);
      const errorMsg =
        err instanceof Error ? err.message : "Analysis calculation failed";
      dispatch({
        type: "SET_ERROR",
        payload: errorMsg,
      });
      dispatch({ type: "SET_STATUS", payload: "error" });
    }
  }, [state.polygon, state.areaHa, state.analysisConfig]);

  const value: AnalysisContextType = {
    state,
    dispatch,
    runAnalysis,
    setPolygon,
    clearPolygon,
    setArea,
    setStatus,
    setResults,
    setProgressStep,
    setConfig,
    setError,
    resetAnalysis,
  };

  return (
    <AnalysisContext.Provider value={value}>
      {children}
    </AnalysisContext.Provider>
  );
}

export function useAnalysis(): AnalysisContextType {
  const context = useContext(AnalysisContext);
  if (!context) {
    throw new Error("useAnalysis must be used within an AnalysisProvider");
  }
  return context;
}


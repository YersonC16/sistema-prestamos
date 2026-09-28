/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_ASSET_SERVICE_URL: string;
  readonly VITE_LOAN_SERVICE_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

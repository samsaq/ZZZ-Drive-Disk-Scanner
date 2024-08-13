import React from "react";
import type { AppProps } from "next/app";
import localFont from "next/font/local";

import "../styles/globals.css";

const IBMDOSFont = localFont({
  src: "../public/fonts/Web437_IBM_BIOS.woff",
  weight: "400",
  variable: "--font-Dos",
});

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <main className={`${IBMDOSFont.className} w-full h-full`}>
      <Component {...pageProps} />
    </main>
  );
}

export default MyApp;

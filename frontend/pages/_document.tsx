import { Html, Head, Main, NextScript } from 'next/document'

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        {/* Title 태그 */}
        <title>BingX Remote Controller - Manage Multiple Accounts Easily</title>

        {/* 기본 메타 태그 */}
        <meta charSet="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta
          name="description"
          content="A platform for placing orders with multiple BingX accounts."
        />

        {/* Open Graph (og) 메타 태그 */}
        <meta property="og:title" content="BingX Remote Controller" />
        <meta
          property="og:description"
          content="A platform for placing orders with multiple BingX accounts."
        />
        <meta property="og:url" content="https://bingx.chihiro.company" />
        <meta property="og:type" content="website" />
        <meta
          property="og:image"
          content="https://bingx.chihiro.company/images/logo.png"
        />
        <meta property="og:image:alt" content="BingX Remote Controller Logo" />

        {/* 기타 추가 설정 */}
        <link rel="icon" href="/images/logo.png" />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  )
}

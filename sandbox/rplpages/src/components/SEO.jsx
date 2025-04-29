import { Helmet } from 'react-helmet-async'

export default function SEO({ title, description, keywords }) {
  return (
    <Helmet>
      <title>{title} | Tokoclone</title>
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:type" content="website" />
    </Helmet>
  )
}
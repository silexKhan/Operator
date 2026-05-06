import { generateStaticParamsFor, importPage } from 'nextra/pages'

export const generateStaticParams = async () => {
  const params = await generateStaticParamsFor('mdx')()
  return params
}

export default async function Page(props: any) {
  const params = await props.params
  const { default: MDXContent, toc, metadata } = await importPage(params.mdx)
  return <MDXContent {...props} toc={toc} metadata={metadata} />
}

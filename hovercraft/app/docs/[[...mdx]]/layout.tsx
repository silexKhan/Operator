import { Layout, Navbar, Footer } from 'nextra-theme-docs'
import { getPageMap } from 'nextra/page-map'
import themeConfig from '../../../theme.config'

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const pageMap = await getPageMap('/docs')
  return (
    <Layout
      navbar={<Navbar logo={themeConfig.logo} />}
      footer={<Footer>{themeConfig.footer?.text}</Footer>}
      pageMap={pageMap}
    >
      {children}
    </Layout>
  )
}

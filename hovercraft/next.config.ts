import nextra from 'nextra'

const withNextra = nextra({
  // theme와 themeConfig 설정
})

const nextConfig = {
  transpilePackages: ["tailwindcss"],
  typescript: {
    ignoreBuildErrors: false,
  }
}

export default withNextra(nextConfig)

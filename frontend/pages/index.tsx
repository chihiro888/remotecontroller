import { useEffect } from 'react'
import { useRouter } from 'next/router'
import { checkAuth } from '../utils/auth'

const Home = () => {
  const router = useRouter()

  const authenticate = async () => {
    const user = await checkAuth(router)
    if (user) {
      router.push('/main')
    } else {
      router.push('/signIn')
    }
  }

  useEffect(() => {
    authenticate()
  }, [])

  return <></>
}

export default Home

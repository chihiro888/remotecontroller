// frontend/utils/auth.ts
import { NextRouter } from 'next/router'

export const checkAuth = async (router: NextRouter) => {
  try {
    const token = localStorage.getItem('jwt') // JWT를 로컬 스토리지에서 가져옴
    if (!token) {
      console.log('토큰이 유효하지 않습니다.')
      router.push('/signIn')
    }

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/getUser`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'x-access-token': token // JWT를 헤더에 포함
        }
      }
    )

    if (response.status !== 200) {
      console.log('토큰이 유효하지 않습니다.')
      router.push('/signIn')
    }

    const data = await response.json()
    return data.data // 사용자 정보 반환
  } catch (error) {
    router.push('/signIn') // JWT가 없거나 유효하지 않은 경우 로그인 페이지로 리다이렉트
    return null
  }
}

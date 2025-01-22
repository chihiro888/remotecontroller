import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import { Input, Button, VStack, Box, Heading } from '@chakra-ui/react'

const Login = () => {
  const [account, setAccount] = useState('')
  const [password, setPassword] = useState('')
  const router = useRouter()

  const handleLogin = async () => {
    try {
      const formData = new FormData()
      formData.append('account', account)
      formData.append('password', password)

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/signIn`,
        {
          method: 'POST',
          body: formData // FormData 객체 사용
        }
      )

      const data = await response.json()
      if (response.status === 200) {
        localStorage.setItem('jwt', data.data.token) // JWT 저장
        router.push('/') // 로그인 성공 시 메인 페이지로 이동
      } else {
        alert(data.message) // 로그인 실패 메시지
      }
    } catch (error) {
      alert('로그인 중 오류가 발생했습니다.')
    }
  }

  return (
    <Box maxW="sm" mx="auto" mt={10} px={6}>
      <Heading as="h1" size="lg" textAlign="center" mb={6}>
        BingX 리모콘
      </Heading>
      <VStack spacing={4}>
        <Input
          placeholder="아이디"
          value={account}
          onChange={(e) => setAccount(e.target.value)}
        />
        <Input
          placeholder="비밀번호"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <Button colorScheme="blue" onClick={handleLogin} w="full">
          로그인
        </Button>
      </VStack>
    </Box>
  )
}

export default Login

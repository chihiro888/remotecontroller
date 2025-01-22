import { useRouter } from 'next/router'
import { Button, VStack, Box, Heading } from '@chakra-ui/react'

const Main = () => {
  const router = useRouter()

  const handleLogout = () => {
    localStorage.removeItem('jwt') // JWT 삭제
    router.push('/login') // 로그인 페이지로 리다이렉트
  }

  return (
    <Box maxW="sm" mx="auto" mt={10}>
      <Heading as="h1" size="lg" textAlign="center" mb={6}>
        Main
      </Heading>
      <VStack spacing={4}>
        <Button colorScheme="red" onClick={handleLogout}>
          로그아웃
        </Button>
      </VStack>
    </Box>
  )
}

export default Main

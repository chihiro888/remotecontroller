import { useEffect, useState } from 'react'
import { useRouter } from 'next/router'
import {
  Box,
  Button,
  VStack,
  Heading,
  Select,
  Input,
  HStack,
  Flex,
  Spacer,
  Text
} from '@chakra-ui/react'
import { checkAuth } from '../utils/auth'

const Main = () => {
  const router = useRouter()
  const [currentAccount, setCurrentAccount] = useState(0)
  const accounts = ['아이디1', '아이디2', '아이디3'] // 예시 계정 리스트

  const handleLogout = () => {
    localStorage.removeItem('jwt') // JWT 삭제
    router.push('/signIn') // 로그인 페이지로 리다이렉트
  }

  const handlePrev = () => {
    setCurrentAccount((prev) => (prev === 0 ? accounts.length - 1 : prev - 1))
  }

  const handleNext = () => {
    setCurrentAccount((prev) => (prev === accounts.length - 1 ? 0 : prev + 1))
  }

  const authenticate = async () => {
    await checkAuth(router)
  }

  useEffect(() => {
    authenticate()
  }, [])

  return (
    <Box>
      {/* AppBar */}
      <Flex
        bg="black"
        color="white"
        p={4}
        align="center"
        position="sticky"
        top="0"
        zIndex="1000"
      >
        <Text fontSize="lg" fontWeight="bold">
          BingX 리모콘
        </Text>
        <Spacer />
        <Button colorScheme="red" size="sm" onClick={handleLogout}>
          로그아웃
        </Button>
      </Flex>

      {/* Main Content */}
      <Box maxW="sm" mx="auto" p={4}>
        <VStack spacing={6}>
          {/* Account Management UI */}
          <Box w="full" borderWidth="1px" borderRadius="lg" p={4} shadow="md">
            <VStack spacing={4}>
              {/* 계정명 */}
              <Text fontSize="lg" fontWeight="bold">
                {accounts[currentAccount]}
              </Text>

              {/* 종목 선택 */}
              <Select placeholder="종목 선택" size="lg">
                <option value="BTCUSDT">BTCUSDT</option>
                <option value="ETHUSDT">ETHUSDT</option>
              </Select>

              {/* 수량 입력 */}
              <Input placeholder="수량 입력" type="number" size="lg" />

              {/* Buy / Sell Buttons */}
              <HStack spacing={4} w="full">
                <Button colorScheme="green" w="full" size="lg">
                  Buy
                </Button>
                <Button colorScheme="red" w="full" size="lg">
                  Sell
                </Button>
              </HStack>
            </VStack>
          </Box>

          <Box w="full" borderWidth="1px" borderRadius="lg" p={4} shadow="md">
            <VStack spacing={4}>
              <Text fontSize="lg" fontWeight="bold">
                주문이력
              </Text>
            </VStack>
          </Box>
        </VStack>
      </Box>

      {/* Bottom Navigation */}
      <Flex
        bg="black"
        p={4}
        align="center"
        justify="space-between"
        position="fixed"
        bottom="0"
        left="0"
        right="0"
        zIndex="1000"
      >
        <Button colorScheme="blue" size="lg" onClick={handlePrev}>
          이전
        </Button>
        <Button colorScheme="blue" size="lg" onClick={handleNext}>
          다음
        </Button>
      </Flex>
    </Box>
  )
}

export default Main

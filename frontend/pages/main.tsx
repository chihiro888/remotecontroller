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
  const [accounts, setAccounts] = useState([]) // Account list from API
  const [currentAccount, setCurrentAccount] = useState(0) // Current selected account
  const [loading, setLoading] = useState(true) // Loading state
  const [error, setError] = useState('') // Error message

  // 추가된 상태
  const [selectedSymbol, setSelectedSymbol] = useState('BTC-USDT') // Selected symbol
  const [quantity, setQuantity] = useState('') // Input quantity
  const [positions, setPositions] = useState(null) // Positions data

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

  const handleClickBuy = async () => {
    console.log('현재 선택된 계정:', accounts[currentAccount].account)
    console.log('선택된 종목:', selectedSymbol)
    console.log('입력된 수량:', quantity)

    if (selectedSymbol === 'BTC-USDT' && Number(quantity) < 0.0001) {
      alert('0.0001 이상의 수량을 입력해주세요.')
      return false
    }
    if (selectedSymbol === 'ETH-USDT' && Number(quantity) < 0.01) {
      alert('0.01 이상의 수량을 입력해주세요.')
      return false
    }

    try {
      const token = localStorage.getItem('jwt') // Get JWT from localStorage
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/buy`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-access-token': token // Add JWT to headers
          },
          body: new URLSearchParams({
            account: accounts[currentAccount].account, // 현재 계정
            symbol: selectedSymbol, // 선택된 종목
            qty: quantity // 입력된 수량
          })
        }
      )

      const result = await response.json()

      if (response.ok) {
        alert(result.message)
      } else {
        alert(result.message || '구매 요청 실패')
      }
    } catch (error) {
      console.error('구매 요청 중 오류 발생:', error)
      alert('시스템 오류가 발생했습니다.')
    }
  }

  const handleClickSell = async () => {
    console.log('현재 선택된 계정:', accounts[currentAccount].account)
    console.log('선택된 종목:', selectedSymbol)
    console.log('입력된 수량:', quantity)

    if (selectedSymbol === 'BTC-USDT' && Number(quantity) < 0.0001) {
      alert('0.0001 이상의 수량을 입력해주세요.')
      return false
    }
    if (selectedSymbol === 'ETH-USDT' && Number(quantity) < 0.01) {
      alert('0.01 이상의 수량을 입력해주세요.')
      return false
    }

    try {
      const token = localStorage.getItem('jwt') // Get JWT from localStorage
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/sell`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-access-token': token // Add JWT to headers
          },
          body: new URLSearchParams({
            account: accounts[currentAccount].account, // 현재 계정
            symbol: selectedSymbol, // 선택된 종목
            qty: quantity // 입력된 수량
          })
        }
      )

      const result = await response.json()

      if (response.ok) {
        alert(result.message)
      } else {
        alert(result.message || '판매 요청 실패')
      }
    } catch (error) {
      console.error('판매 요청 중 오류 발생:', error)
      alert('시스템 오류가 발생했습니다.')
    }
  }

  const fetchPositions = async () => {
    try {
      const token = localStorage.getItem('jwt') // Get JWT from localStorage
      const account = accounts[currentAccount]?.account // Get current account

      if (!account) return

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/getPosition?account=${account}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'x-access-token': token
          }
        }
      )

      if (response.ok) {
        const data = await response.json()
        console.log('data.data => ', data.data)
        setPositions(data.data)
      } else {
        const result = await response.json()
        console.error(result.message || 'Failed to fetch positions')
      }
    } catch (error) {
      console.error('Error fetching positions:', error)
    }
  }

  useEffect(() => {
    fetchPositions()

    const interval = setInterval(() => {
      fetchPositions()
    }, 3000) // Call every 3 seconds

    return () => clearInterval(interval)
  }, [currentAccount, accounts])

  const authenticate = async () => {
    await checkAuth(router)
  }

  const fetchAccounts = async () => {
    try {
      const token = localStorage.getItem('jwt') // Get JWT from localStorage
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/getAccountList`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'x-access-token': token
          }
        }
      )

      if (response.ok) {
        const data = await response.json()
        setAccounts(data.data || [])
      } else {
        const result = await response.json()
        setError(result.message || 'Error fetching accounts.')
      }
    } catch (e) {
      console.error('Failed to fetch accounts:', e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    authenticate()
    fetchAccounts()
  }, [])

  if (loading) {
    return (
      <Box>
        <Text>Loading...</Text>
      </Box>
    )
  }

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
      {accounts.length !== 0 ? (
        <Box maxW="sm" mx="auto" p={4}>
          <VStack spacing={6}>
            {/* Account Management UI */}
            <Box w="full" borderWidth="1px" borderRadius="lg" p={4} shadow="md">
              <VStack spacing={4}>
                {/* 계정명 */}
                <Text fontSize="lg" fontWeight="bold">
                  {accounts[currentAccount].account}
                </Text>

                {/* 종목 선택 */}
                <Select
                  value={selectedSymbol}
                  size="lg"
                  onChange={(e) => setSelectedSymbol(e.target.value)}
                >
                  <option value="BTC-USDT">BTC-USDT</option>
                  <option value="ETH-USDT">ETH-USDT</option>
                </Select>

                {/* 수량 입력 */}
                <Input
                  placeholder="수량 입력"
                  type="number"
                  size="lg"
                  value={quantity}
                  onChange={(e) => setQuantity(e.target.value)}
                />

                {/* Buy / Sell Buttons */}
                <HStack spacing={4} w="full">
                  <Button
                    colorScheme="green"
                    w="full"
                    size="lg"
                    onClick={handleClickBuy}
                  >
                    Buy
                  </Button>
                  <Button
                    colorScheme="red"
                    w="full"
                    size="lg"
                    onClick={handleClickSell}
                  >
                    Sell
                  </Button>
                </HStack>
              </VStack>
            </Box>

            {positions && positions['btc'] && positions['btc'].length > 0 ? (
              <>
                <Box
                  w="full"
                  borderWidth="1px"
                  borderRadius="lg"
                  p={4}
                  shadow="md"
                >
                  <Text fontSize="lg" fontWeight="bold">
                    BTC 포지션
                  </Text>
                  <Flex gap={2}>
                    <Text>{positions['btc'][0]['leverage']}x</Text>
                    <Text
                      style={{
                        color:
                          positions['btc'][0]['positionSide'] === 'LONG'
                            ? 'green'
                            : 'red'
                      }}
                    >
                      {positions['btc'][0]['positionSide']}
                    </Text>
                  </Flex>
                  <Flex gap={2}>
                    <Text>평단가: {positions['btc'][0]['avgPrice']}</Text>
                    <Text>
                      청산가: {positions['btc'][0]['liquidationPrice']}
                    </Text>
                  </Flex>
                  <Flex gap={2}>
                    <Text>
                      미실현손익:{' '}
                      <span
                        style={{
                          color:
                            positions['btc'][0]['unrealizedProfit'] < 0
                              ? 'red'
                              : 'green'
                        }}
                      >
                        {positions['btc'][0]['unrealizedProfit']} (
                        {(positions['btc'][0]['pnlRatio'] * 100).toFixed(2)} %)
                      </span>
                    </Text>
                  </Flex>
                  <Flex gap={2}>
                    수량:{' '}
                    <Text fontWeight={'bold'}>
                      {positions['btc'][0]['availableAmt']} BTC
                    </Text>
                  </Flex>
                </Box>
              </>
            ) : (
              <></>
            )}

            {positions && positions['eth'] && positions['eth'].length > 0 ? (
              <>
                <Box
                  w="full"
                  borderWidth="1px"
                  borderRadius="lg"
                  p={4}
                  shadow="md"
                >
                  <Text fontSize="lg" fontWeight="bold">
                    ETH 포지션
                  </Text>
                  <Flex gap={2}>
                    <Text>{positions['eth'][0]['leverage']}x</Text>
                    <Text
                      style={{
                        color:
                          positions['eth'][0]['positionSide'] === 'LONG'
                            ? 'green'
                            : 'red'
                      }}
                    >
                      {positions['eth'][0]['positionSide']}
                    </Text>
                  </Flex>
                  <Flex gap={2}>
                    <Text>평단가: {positions['eth'][0]['avgPrice']}</Text>
                    <Text>
                      청산가: {positions['eth'][0]['liquidationPrice']}
                    </Text>
                  </Flex>
                  <Flex gap={2}>
                    <Text>
                      미실현손익:{' '}
                      <span
                        style={{
                          color:
                            positions['eth'][0]['unrealizedProfit'] < 0
                              ? 'red'
                              : 'green'
                        }}
                      >
                        {positions['eth'][0]['unrealizedProfit']} (
                        {(positions['eth'][0]['pnlRatio'] * 100).toFixed(2)} %)
                      </span>
                    </Text>
                  </Flex>
                  <Flex gap={2}>
                    수량:{' '}
                    <Text fontWeight={'bold'}>
                      {positions['eth'][0]['availableAmt']} ETH
                    </Text>
                  </Flex>
                </Box>
              </>
            ) : (
              <></>
            )}
          </VStack>
        </Box>
      ) : (
        <Box textAlign={'center'} mt={10}>
          <Text fontSize={'lg'}>등록된 계정이 없습니다</Text>
        </Box>
      )}

      <Box mb={15}>.</Box>
      <Box mb={15}>.</Box>
      <Box mb={15}>.</Box>
      <Box mb={15}>.</Box>

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

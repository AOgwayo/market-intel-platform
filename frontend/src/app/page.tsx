'use client';

import {
  Box,
  Flex,
  Heading,
  Text,
  Button,
  Container,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Card,
  CardHeader,
  CardBody,
  Badge,
  VStack,
  HStack,
  useColorModeValue,
} from '@chakra-ui/react';
import { useState, useEffect } from 'react';

export default function HomePage() {
  const [apiHealth, setApiHealth] = useState<string>('checking...');
  const bgColor = useColorModeValue('gray.50', 'gray.900');

  useEffect(() => {
    // Check API health
    fetch('/api/health')
      .then((res) => res.json())
      .then((data) => setApiHealth(data.status))
      .catch(() => setApiHealth('offline'));
  }, []);

  return (
    <Box minH="100vh" bg={bgColor}>
      {/* Header */}
      <Box bg="white" shadow="sm" px={4} py={4}>
        <Container maxW="container.xl">
          <Flex justify="space-between" align="center">
            <Heading size="lg" color="brand.600">
              Market Intel Platform
            </Heading>
            <HStack spacing={4}>
              <Badge colorScheme={apiHealth === 'healthy' ? 'green' : 'red'}>
                API: {apiHealth}
              </Badge>
              <Button colorScheme="brand" size="sm">
                Login
              </Button>
            </HStack>
          </Flex>
        </Container>
      </Box>

      {/* Main Content */}
      <Container maxW="container.xl" py={8}>
        <VStack spacing={8} align="stretch">
          {/* Hero Section */}
          <Box textAlign="center" py={8}>
            <Heading size="2xl" mb={4}>
              Welcome to Market Intelligence Platform
            </Heading>
            <Text fontSize="xl" color="gray.600" maxW="2xl" mx="auto">
              A comprehensive platform for market analysis, algorithmic trading,
              and real-time market intelligence powered by advanced analytics.
            </Text>
          </Box>

          {/* Stats Grid */}
          <SimpleGrid columns={{ base: 1, md: 4 }} spacing={6}>
            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>Active Strategies</StatLabel>
                  <StatNumber>4</StatNumber>
                  <StatHelpText>Mean reversion, Momentum, etc.</StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>Market Symbols</StatLabel>
                  <StatNumber>50+</StatNumber>
                  <StatHelpText>Stocks, ETFs, Crypto</StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>Daily Signals</StatLabel>
                  <StatNumber>150+</StatNumber>
                  <StatHelpText>Real-time generation</StatHelpText>
                </Stat>
              </CardBody>
            </Card>

            <Card>
              <CardBody>
                <Stat>
                  <StatLabel>Uptime</StatLabel>
                  <StatNumber>99.9%</StatNumber>
                  <StatHelpText>Last 30 days</StatHelpText>
                </Stat>
              </CardBody>
            </Card>
          </SimpleGrid>

          {/* Feature Cards */}
          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
            <Card>
              <CardHeader>
                <Heading size="md">Strategy Engine</Heading>
              </CardHeader>
              <CardBody>
                <Text>
                  Advanced algorithmic trading strategies with real-time signal
                  generation and backtesting capabilities.
                </Text>
                <Button mt={4} colorScheme="brand" size="sm">
                  View Strategies
                </Button>
              </CardBody>
            </Card>

            <Card>
              <CardHeader>
                <Heading size="md">Market Data</Heading>
              </CardHeader>
              <CardBody>
                <Text>
                  Real-time market data ingestion from multiple sources with
                  comprehensive historical data storage.
                </Text>
                <Button mt={4} colorScheme="brand" size="sm">
                  Explore Data
                </Button>
              </CardBody>
            </Card>

            <Card>
              <CardHeader>
                <Heading size="md">Trading Interface</Heading>
              </CardHeader>
              <CardBody>
                <Text>
                  Integrated trading interface with risk management, order
                  routing, and portfolio tracking.
                </Text>
                <Button mt={4} colorScheme="brand" size="sm">
                  Start Trading
                </Button>
              </CardBody>
            </Card>
          </SimpleGrid>
        </VStack>
      </Container>

      {/* Footer */}
      <Box bg="gray.800" color="white" py={8} mt={16}>
        <Container maxW="container.xl">
          <Text textAlign="center">
            © 2024 Market Intel Platform. Built with Next.js and FastAPI.
          </Text>
        </Container>
      </Box>
    </Box>
  );
}
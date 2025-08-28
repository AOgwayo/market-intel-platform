import { ChakraProvider, Heading, Text, Box } from "@chakra-ui/react";

export default function Home() {
  return (
    <ChakraProvider>
      <Box p={8}>
        <Heading size="lg" mb={4}>Market Intelligence Platform</Heading>
        <Text>Frontend scaffold is running. Build dashboard components here.</Text>
      </Box>
    </ChakraProvider>
  );
}
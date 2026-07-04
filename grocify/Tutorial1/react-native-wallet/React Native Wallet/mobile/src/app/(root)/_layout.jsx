import { View, Text } from "react-native";
import React from "react";
import { useUser } from "@clerk/clerk-expo";
import { Redirect, Stack } from "expo-router";

const Layout = () => {
  const { isSignedIn } = useUser();

  if (!isSignedIn) return <Redirect href={"/sign-in"} />;
  return <Stack screenOptions={{ headerShown: false }} />;
};

export default Layout;

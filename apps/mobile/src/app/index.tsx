import { View, Text, StyleSheet } from "react-native";
import { Link } from "expo-router";

export default function Home() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>RapiDrop</Text>
      <Text style={styles.subtitle}>Delivery Intelligence</Text>
      <Link href="/stores" style={styles.link}>
        Ver lojas próximas
      </Link>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
    backgroundColor: "#fff",
  },
  title: {
    fontSize: 32,
    fontWeight: "bold",
    color: "#2563eb",
  },
  subtitle: {
    fontSize: 16,
    color: "#6b7280",
    marginTop: 8,
  },
  link: {
    marginTop: 24,
    fontSize: 16,
    color: "#2563eb",
    textDecorationLine: "underline",
  },
});

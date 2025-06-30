import { fetchDigitalTwin } from "$lib/api"

export async function load({ params }) {
  try {
    const digitalTwin = await fetchDigitalTwin(params.id)
    return {
      id: params.id,
      digitalTwin,
      error: null,
    }
  } catch (error) {
    console.error("Failed to load digital twin:", error)
    return {
      id: params.id,
      digitalTwin: null,
      error: "Kon digital twin niet laden. Controleer of de API server draait.",
    }
  }
}

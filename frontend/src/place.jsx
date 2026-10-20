import { createContext, useContext, useEffect, useState } from "react";

export const PRESETS = [
  { label: "Hyderabad (city centre)", city: "Hyderabad", lat: 17.385, lng: 78.4867 },
  { label: "Madhapur", city: "Hyderabad", lat: 17.4435, lng: 78.3772 },
  { label: "Gachibowli", city: "Hyderabad", lat: 17.4401, lng: 78.3489 },
  { label: "Ameerpet", city: "Hyderabad", lat: 17.4375, lng: 78.4483 },
  { label: "Banjara Hills", city: "Hyderabad", lat: 17.4156, lng: 78.4347 },
  { label: "Kukatpally", city: "Hyderabad", lat: 17.4948, lng: 78.3996 },
  { label: "Secunderabad", city: "Hyderabad", lat: 17.4399, lng: 78.4983 },
];

const KEY = "place";
const PlaceContext = createContext(null);

function loadSaved() {
  try {
    return JSON.parse(localStorage.getItem(KEY));
  } catch {
    return null;
  }
}

export function PlaceProvider({ children }) {
  const [place, setPlace] = useState(loadSaved() || PRESETS[0]);
  const [detecting, setDetecting] = useState(false);

  function choose(next) {
    setPlace(next);
    try {
      localStorage.setItem(KEY, JSON.stringify(next));
    } catch {
      /* storage unavailable */
    }
  }

  function detect() {
    if (!navigator.geolocation) return;
    setDetecting(true);
    navigator.geolocation.getCurrentPosition(
      async ({ coords }) => {
        let label = "Current location";
        let city = "Hyderabad";
        try {
          const res = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${coords.latitude}&lon=${coords.longitude}`
          );
          const a = (await res.json()).address || {};
          city = a.city || a.town || a.state_district || city;
          label = [a.suburb || a.neighbourhood, city].filter(Boolean).join(", ");
        } catch {
          /* keep defaults */
        }
        choose({ label, city, lat: coords.latitude, lng: coords.longitude });
        setDetecting(false);
      },
      () => setDetecting(false),
      { timeout: 10000 }
    );
  }

  useEffect(() => {
    if (!loadSaved()) detect();
  }, []);

  return (
    <PlaceContext.Provider value={{ place, choose, detect, detecting }}>
      {children}
    </PlaceContext.Provider>
  );
}

export const usePlace = () => useContext(PlaceContext);

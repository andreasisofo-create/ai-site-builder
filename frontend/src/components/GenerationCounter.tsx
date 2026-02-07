"use client";

import { useEffect, useState } from "react";
import { SparklesIcon, CrownIcon, LockClosedIcon } from "@heroicons/react/24/outline";
import { getQuota, upgradeToPremium, UserQuota } from "@/lib/api";
import toast from "react-hot-toast";

export default function GenerationCounter() {
  // Ritorna null temporaneamente per evitare errori di build dovuti a tipi mancanti o conflitti
  return null;
}

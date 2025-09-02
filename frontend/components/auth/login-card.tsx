"use client"

import { useState } from "react"
import {
  GoogleAuthProvider,
  signInWithPopup,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
} from "firebase/auth"
import { getFirebaseAuth } from "@/lib/firebase"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { useToast } from "@/hooks/use-toast"

export function LoginCard() {
  const auth = getFirebaseAuth()
  const { toast } = useToast()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)

  async function handleGoogle() {
    setLoading(true)
    try {
      const provider = new GoogleAuthProvider()
      await signInWithPopup(auth, provider)
    } catch (e: any) {
      toast({ title: "Google sign-in failed", description: e?.message ?? "Try again.", variant: "destructive" })
    } finally {
      setLoading(false)
    }
  }

  async function handleEmailSignIn() {
    setLoading(true)
    try {
      await signInWithEmailAndPassword(auth, email, password)
    } catch (e: any) {
      toast({ title: "Sign in failed", description: e?.message ?? "Check your credentials.", variant: "destructive" })
    } finally {
      setLoading(false)
    }
  }

  async function handleEmailSignUp() {
    setLoading(true)
    try {
      await createUserWithEmailAndPassword(auth, email, password)
    } catch (e: any) {
      toast({ title: "Sign up failed", description: e?.message ?? "Check your details.", variant: "destructive" })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-balance">Welcome to Pennywise</CardTitle>
        <CardDescription className="text-pretty">
          Sign in to view your spending analytics and manage transactions.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-3">
          <Input
            type="email"
            placeholder="Email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <Input
            type="password"
            placeholder="Password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <div className="flex flex-col gap-2">
            <Button className="w-full" onClick={handleEmailSignIn} disabled={loading}>
              Sign in
            </Button>
            <Button className="w-full" variant="secondary" onClick={handleEmailSignUp} disabled={loading}>
              Sign up
            </Button>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Separator className="flex-1" />
          <span className="text-xs text-muted-foreground">or</span>
          <Separator className="flex-1" />
        </div>

        <Button variant="outline" className="w-full bg-transparent" onClick={handleGoogle} disabled={loading}>
          Continue with Google
        </Button>

        {/* TODO: Add Phone OTP flow upon confirmation */}
      </CardContent>
    </Card>
  )
}

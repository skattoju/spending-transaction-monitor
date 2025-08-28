import { createFileRoute } from '@tanstack/react-router'
import { useAuth } from 'react-oidc-context'
import { useEffect } from 'react'
import { Button } from '../components/atoms/button/button'
import { Card } from '../components/atoms/card/card'
import { Logo } from '../components/logo/logo'

export const Route = createFileRoute('/login')({
  component: LoginPage,
})

function LoginPage() {
  const auth = useAuth()

  useEffect(() => {
    // If already authenticated, redirect to home
    if (auth.isAuthenticated) {
      window.location.href = '/'
    }
  }, [auth.isAuthenticated])

  const handleLogin = () => {
    auth.signinRedirect()
  }

  if (auth.isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="max-w-md w-full p-8 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading authentication...</p>
        </Card>
      </div>
    )
  }

  if (auth.error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="max-w-md w-full p-8 text-center space-y-4">
          <h2 className="text-xl font-semibold text-red-600">Authentication Error</h2>
          <p className="text-gray-600">
            {auth.error.message || 'An error occurred during authentication'}
          </p>
          <Button onClick={() => window.location.reload()} variant="outline" className="w-full">
            Try Again
          </Button>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <Card className="max-w-md w-full p-8 space-y-6">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <Logo />
          </div>
          <div>
            <h2 className="text-2xl font-bold">Welcome to Spending Monitor</h2>
            <p className="text-gray-600 mt-2">
              Sign in to access your transaction dashboard and manage alerts
            </p>
          </div>
        </div>

        {/* Login Section */}
        <div className="space-y-4">
          <Button onClick={handleLogin} className="w-full" size="lg">
            Sign In with Keycloak
          </Button>
          
          <div className="text-center">
            <p className="text-sm text-gray-500">
              Secure authentication powered by OpenID Connect
            </p>
          </div>
        </div>

        {/* Features Preview */}
        <div className="border-t pt-6">
          <h3 className="text-sm font-medium text-gray-900 mb-3">What you'll get:</h3>
          <ul className="text-sm text-gray-600 space-y-2">
            <li className="flex items-center">
              <svg className="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Real-time transaction monitoring
            </li>
            <li className="flex items-center">
              <svg className="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              AI-powered spending alerts
            </li>
            <li className="flex items-center">
              <svg className="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Secure role-based access
            </li>
          </ul>
        </div>
      </Card>
    </div>
  )
}

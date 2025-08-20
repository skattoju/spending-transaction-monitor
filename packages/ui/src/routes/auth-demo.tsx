import { createFileRoute } from '@tanstack/react-router'
import { useAuth } from 'react-oidc-context'
import { useState } from 'react'
import { Button } from '../components/atoms/button/button'
import { Card } from '../components/atoms/card/card'

export const Route = createFileRoute('/auth-demo')({
  component: AuthDemoPage,
})

interface ApiResponse {
  message: string;
  authenticated?: boolean;
  user?: any;
  error?: string;
  status?: number;
  statusText?: string;
}

function AuthDemoPage() {
  const auth = useAuth()
  const [apiResponses, setApiResponses] = useState<Record<string, ApiResponse>>({})
  const [loading, setLoading] = useState<Record<string, boolean>>({})

  const testEndpoint = async (endpoint: string, requiresAuth: boolean = true) => {
    setLoading(prev => ({ ...prev, [endpoint]: true }))
    
    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json'
      }
      
      if (requiresAuth && auth.user?.access_token) {
        headers.Authorization = `Bearer ${auth.user.access_token}`
      }
      
      const response = await fetch(`http://localhost:8000/auth-demo${endpoint}`, {
        headers
      })
      
      const data = await response.json()
      
      setApiResponses(prev => ({
        ...prev,
        [endpoint]: { 
          ...data, 
          error: response.ok ? undefined : data.detail,
          status: response.status,
          statusText: response.statusText
        }
      }))
    } catch (error) {
      setApiResponses(prev => ({
        ...prev,
        [endpoint]: { 
          message: 'Request failed', 
          error: error instanceof Error ? error.message : 'Unknown error' 
        }
      }))
    } finally {
      setLoading(prev => ({ ...prev, [endpoint]: false }))
    }
  }

  // Redirect to login if not authenticated
  if (!auth.isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="max-w-md w-full p-8 text-center space-y-4">
          <h2 className="text-xl font-semibold">Authentication Required</h2>
          <p className="text-gray-600">
            You need to be logged in to access this demo page.
          </p>
          <Button 
            onClick={() => auth.signinRedirect()}
            className="w-full"
          >
            Sign In
          </Button>
        </Card>
      </div>
    )
  }

  const endpoints = [
    { path: '/public', name: 'Public Endpoint', requiresAuth: false, description: 'Accessible without authentication' },
    { path: '/profile', name: 'Profile (Optional Auth)', requiresAuth: false, description: 'Shows different content based on auth status' },
    { path: '/protected', name: 'Protected Endpoint', requiresAuth: true, description: 'Requires valid JWT token' },
    { path: '/user-only', name: 'User Role Required', requiresAuth: true, description: 'Requires "user" role or higher' },
    { path: '/admin-only', name: 'Admin Role Required', requiresAuth: true, description: 'Requires "admin" role' },
    { path: '/token-info', name: 'Token Information', requiresAuth: true, description: 'Shows JWT token claims and details' },
  ]

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <Card className="p-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold">Authentication Demo</h1>
              <p className="text-gray-600 mt-1">
                Test API endpoints with JWT authentication
              </p>
            </div>
            <Button 
              onClick={() => auth.signoutRedirect()}
              variant="outline"
            >
              Logout
            </Button>
          </div>
        </Card>

        {/* User Info */}
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Current User</h2>
          <div className="bg-blue-50 border border-blue-200 rounded p-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <strong>Email:</strong> {auth.user?.profile?.email}
              </div>
              <div>
                <strong>Username:</strong> {auth.user?.profile?.preferred_username}
              </div>
              <div>
                <strong>User ID:</strong> {auth.user?.profile?.sub}
              </div>
              <div>
                <strong>Roles:</strong> {(auth.user?.profile as any)?.realm_access?.roles?.join(', ') || 'None'}
              </div>
            </div>
          </div>
        </Card>

        {/* API Testing */}
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">API Endpoint Testing</h2>
          <div className="space-y-4">
            {endpoints.map(({ path, name, requiresAuth, description }) => (
              <div key={path} className="border rounded p-4">
                <div className="flex justify-between items-center mb-3">
                  <div>
                    <h3 className="font-medium">{name}</h3>
                    <p className="text-sm text-gray-600">
                      GET /auth-demo{path} 
                      {requiresAuth ? ' (Requires Auth)' : ' (Public)'}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">{description}</p>
                  </div>
                  <Button
                    onClick={() => testEndpoint(path, requiresAuth)}
                    disabled={loading[path]}
                    size="sm"
                  >
                    {loading[path] ? 'Testing...' : 'Test'}
                  </Button>
                </div>
                
                {apiResponses[path] && (
                  <div className="mt-3 space-y-2">
                    {apiResponses[path].error && (
                      <div className="p-3 bg-red-50 border border-red-200 rounded text-sm">
                        <div className="font-medium text-red-800">
                          Error {apiResponses[path].status || ''}: {apiResponses[path].error}
                        </div>
                        {apiResponses[path].statusText && (
                          <div className="text-red-600 text-xs mt-1">
                            {apiResponses[path].statusText}
                          </div>
                        )}
                      </div>
                    )}
                    <div className={`p-3 rounded text-sm border ${
                      apiResponses[path].error 
                        ? 'bg-gray-50 border-gray-200' 
                        : 'bg-green-50 border-green-200'
                    }`}>
                      <details>
                        <summary className="cursor-pointer font-medium">
                          {apiResponses[path].error ? 'Full Response' : 'Response'} 
                          {apiResponses[path].status && (
                            <span className={`ml-2 px-2 py-1 rounded text-xs ${
                              apiResponses[path].status < 300 ? 'bg-green-100 text-green-800' : 
                              apiResponses[path].status < 400 ? 'bg-yellow-100 text-yellow-800' : 
                              'bg-red-100 text-red-800'
                            }`}>
                              {apiResponses[path].status}
                            </span>
                          )}
                        </summary>
                        <pre className="whitespace-pre-wrap mt-2 text-xs">
                          {JSON.stringify(apiResponses[path], null, 2)}
                        </pre>
                      </details>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
          
          <div className="mt-6 pt-4 border-t">
            <Button
              onClick={() => endpoints.forEach(ep => testEndpoint(ep.path, ep.requiresAuth))}
              variant="outline"
              className="w-full"
            >
              Test All Endpoints
            </Button>
          </div>
        </Card>
      </div>
    </div>
  )
}
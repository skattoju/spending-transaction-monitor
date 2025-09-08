import { Bell, Menu, CreditCard } from 'lucide-react';
import { Button } from '../atoms/button/button';
import { UserAvatar } from '../user-avatar/user-avatar';
import { cn } from '../../lib/utils';
import { Link } from '@tanstack/react-router';
import { useCurrentUser } from '../../hooks/user';

export interface DashboardHeaderProps {
  className?: string;
  onMenuClick?: () => void;
}

export function DashboardHeader({ className, onMenuClick }: DashboardHeaderProps) {
  const { user, logout } = useCurrentUser();

  return (
    <header className={cn('border-b border-border bg-card', className)}>
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Navigation */}
          <div className="flex items-center gap-8">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="icon"
                className="md:hidden"
                onClick={onMenuClick}
              >
                <Menu className="h-5 w-5" />
              </Button>

              <Link to="/" className="flex items-center gap-2">
                <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                  <CreditCard className="h-5 w-5 text-primary-foreground" />
                </div>
                <span className="font-semibold text-xl text-foreground hidden sm:block">
                  TransactionGuard
                </span>
              </Link>
            </div>

            <nav className="hidden md:flex items-center gap-6">
              <Link
                to="/"
                className="text-foreground hover:text-primary transition-colors text-sm font-medium"
                activeProps={{ className: 'text-primary' }}
              >
                Dashboard
              </Link>
              <Link
                to="/transactions"
                className="text-muted-foreground hover:text-primary transition-colors text-sm font-medium"
                activeProps={{ className: 'text-primary' }}
              >
                Transactions
              </Link>
              <Link
                to="/alerts"
                className="text-muted-foreground hover:text-primary transition-colors text-sm font-medium"
                activeProps={{ className: 'text-primary' }}
              >
                Alert Rules
              </Link>
            </nav>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="icon" className="relative rounded-full">
              <Bell className="h-5 w-5" />
              <span className="absolute -top-1 -right-1 h-2 w-2 bg-error rounded-full" />
            </Button>

            <UserAvatar
              userName={user?.fullName}
              userEmail={user?.email}
              onSettingsClick={() => {
                // TODO: Navigate to settings page
                console.log('Settings clicked');
              }}
              onLogoutClick={() => {
                logout();
                console.log('User logged out');
              }}
            />
          </div>
        </div>
      </div>
    </header>
  );
}

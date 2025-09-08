import { Button } from '../atoms/button/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../atoms/dropdown-menu/dropdown-menu';
import { Avatar, AvatarFallback, AvatarImage } from '../atoms/avatar/avatar';
import { Settings, LogOut, User, ChevronDown } from 'lucide-react';
import { cn } from '../../lib/utils';

export interface UserAvatarProps {
  className?: string;
  userName?: string;
  userEmail?: string;
  avatarUrl?: string;
  onSettingsClick?: () => void;
  onLogoutClick?: () => void;
}

export function UserAvatar({
  className,
  userName,
  userEmail,
  avatarUrl,
  onSettingsClick,
  onLogoutClick,
}: UserAvatarProps) {
  // Use fallbacks when user data is not provided
  const displayName = userName || 'Loading...';
  const displayEmail = userEmail || 'user@example.com';
  const isLoading = !userName;
  
  const initials = displayName && displayName !== 'Loading...'
    ? displayName
        .split(' ')
        .map((name) => name.charAt(0))
        .join('')
        .toUpperCase()
        .slice(0, 2)
    : '?';

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          className={cn(
            'relative h-10 w-auto rounded-full px-3 py-1',
            'hover:bg-muted focus:bg-muted',
            className,
          )}
        >
          <div className="flex items-center gap-2">
            <div className="relative">
              <Avatar className="h-8 w-8">
                <AvatarImage src={avatarUrl} alt={displayName} />
                <AvatarFallback className="text-xs font-medium">
                  {initials}
                </AvatarFallback>
              </Avatar>
            </div>
            <div className="hidden sm:block text-left">
              <p className={`text-sm font-medium ${isLoading ? 'text-muted-foreground animate-pulse' : 'text-foreground'}`}>
                {displayName}
              </p>
            </div>
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          </div>
        </Button>
      </DropdownMenuTrigger>

      <DropdownMenuContent className="w-64" align="end" forceMount>
        <DropdownMenuLabel className="p-0 font-normal">
          <div className="flex items-center gap-3 px-3 py-2">
            <Avatar className="h-10 w-10">
              <AvatarImage src={avatarUrl} alt={displayName} />
              <AvatarFallback className="text-sm font-medium">
                {initials}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <p className={`text-sm font-medium truncate ${isLoading ? 'text-muted-foreground animate-pulse' : 'text-foreground'}`}>
                {displayName}
              </p>
              <p className="text-xs text-muted-foreground truncate">{displayEmail}</p>
            </div>
          </div>
        </DropdownMenuLabel>

        <DropdownMenuSeparator />

        <DropdownMenuItem onClick={onSettingsClick}>
          <Settings className="h-4 w-4 mr-2" />
          Settings
        </DropdownMenuItem>

        <DropdownMenuItem
          onClick={() => {
            // TODO: Add profile/account management
            console.log('Profile clicked');
          }}
        >
          <User className="h-4 w-4 mr-2" />
          Profile
        </DropdownMenuItem>

        <DropdownMenuSeparator />

        <DropdownMenuItem
          className="text-error focus:text-error"
          onClick={onLogoutClick}
        >
          <LogOut className="h-4 w-4 mr-2" />
          Log out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

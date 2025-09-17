import { useState } from 'react';
import { createFileRoute } from '@tanstack/react-router';
import { Card } from '../components/atoms/card/card';
import { Button } from '../components/atoms/button/button';
import { Badge } from '../components/atoms/badge/badge';
import { AlertRuleForm } from '../components/alert-rule-form/alert-rule-form';
import { ProtectedRoute } from '../components/auth/ProtectedRoute';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../components/atoms/dialog/dialog';
import { Bell, Pause, Play, Trash2 } from 'lucide-react';
import {
  useAlertRules,
  useCreateAlertRule,
  useToggleAlertRule,
  useDeleteAlertRule,
} from '../hooks/transactions';
import { cn } from '../lib/utils';
import { statusColors } from '../lib/colors';
import type { CreateAlertRuleInput } from '../schemas/alert-rule';

export const Route = createFileRoute('/alerts')({
  component: () => (
    <ProtectedRoute>
      <AlertsPage />
    </ProtectedRoute>
  ),
});

function AlertsPage() {
  const { data: rules, isLoading } = useAlertRules();
  const createRule = useCreateAlertRule();
  const toggleRule = useToggleAlertRule();
  const deleteRule = useDeleteAlertRule();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [ruleToDelete, setRuleToDelete] = useState<{ id: string; name: string } | null>(
    null,
  );

  const handleCreateRule = async (data: CreateAlertRuleInput) => {
    try {
      await createRule.mutateAsync(data.rule);
    } catch (error) {
      console.error('Failed to create rule:', error);
      // TODO: Show error toast notification
    }
  };

  const handleToggleRule = (ruleId: string) => {
    toggleRule.mutate(ruleId);
  };

  const openDeleteDialog = (ruleId: string, ruleName: string) => {
    setRuleToDelete({ id: ruleId, name: ruleName });
    setDeleteDialogOpen(true);
  };

  const closeDeleteDialog = () => {
    setDeleteDialogOpen(false);
    setRuleToDelete(null);
  };

  const handleDeleteRule = () => {
    if (!ruleToDelete) return;

    deleteRule.mutate(ruleToDelete.id, {
      onSuccess: () => {
        closeDeleteDialog();
      },
    });
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="text-center mt-4 mb-8">
        <h1 className="text-3xl font-bold text-foreground mb-2">Alert Rules</h1>
        <p className="text-muted-foreground">
          Create and manage your transaction monitoring rules with natural language
        </p>
      </div>

      {/* Alert Rule Form */}
      <div className="mb-8">
        <AlertRuleForm
          onSubmit={handleCreateRule}
          isSubmitting={createRule.isPending}
        />
      </div>

      {/* Active Rules */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-foreground">Active Rules</h2>
        </div>

        {isLoading ? (
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <Card key={i} className="p-4">
                <div className="animate-pulse">
                  <div className="h-5 bg-muted rounded w-3/4 mb-2" />
                  <div className="h-4 bg-muted rounded w-1/2" />
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <div className="space-y-3">
            {rules?.map((rule) => (
              <Card
                key={rule.id}
                className={cn(
                  'border-l-4 p-4',
                  rule.status === 'active' ? 'border-l-primary' : 'border-l-muted',
                )}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <Bell className="h-4 w-4 text-muted-foreground" />
                      <p className="font-medium text-foreground">{rule.rule}</p>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <span>Triggered {rule.triggered} times</span>
                      <span>•</span>
                      <span>Last: {rule.last_triggered}</span>
                      {rule.status === 'inactive' && (
                        <span className="text-orange-600 font-medium">• Paused</span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge
                      variant="secondary"
                      className={cn(
                        'capitalize',
                        statusColors[rule.status as keyof typeof statusColors]?.badge ||
                          'bg-muted text-muted-foreground',
                      )}
                    >
                      {rule.status}
                    </Badge>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleToggleRule(rule.id)}
                      disabled={toggleRule.isPending}
                      title={
                        rule.status === 'active'
                          ? 'Pause alert rule'
                          : 'Resume alert rule'
                      }
                    >
                      {rule.status === 'active' ? (
                        <Pause className="h-4 w-4" />
                      ) : (
                        <Play className="h-4 w-4 text-green-600" />
                      )}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => openDeleteDialog(rule.id, rule.rule)}
                      disabled={deleteRule.isPending}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </div>
              </Card>
            ))}

            {rules?.length === 0 && (
              <Card className="p-8 text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-muted mb-3">
                  <Bell className="h-6 w-6 text-muted-foreground" />
                </div>
                <p className="text-muted-foreground">No alert rules configured yet</p>
                <p className="text-sm text-muted-foreground mt-1">
                  Start by creating your first rule above
                </p>
              </Card>
            )}
          </div>
        )}
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Alert Rule</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete the alert rule "{ruleToDelete?.name}"?
              This action cannot be undone and will also delete all associated
              notifications.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={closeDeleteDialog}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteRule}
              disabled={deleteRule.isPending}
            >
              {deleteRule.isPending ? 'Deleting...' : 'Delete Rule'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

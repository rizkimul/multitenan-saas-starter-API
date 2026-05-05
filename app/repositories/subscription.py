import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import Subscription, SubscriptionStatus


class SubscriptionRepository:
    """Data access layer for workspace subscriptions."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_workspace_id(self, workspace_id: uuid.UUID) -> Subscription | None:
        """Fetch the subscription for a workspace.

        Args:
            workspace_id: The workspace UUID.

        Returns:
            The Subscription, or None if not yet created.
        """
        result = await self.session.execute(
            select(Subscription).where(Subscription.workspace_id == workspace_id)
        )
        return result.scalars().first()

    async def get_by_stripe_customer_id(self, customer_id: str) -> Subscription | None:
        """Fetch a subscription by its Stripe customer ID.

        Args:
            customer_id: The Stripe customer ID (e.g. ``cus_...``).

        Returns:
            The matching Subscription, or None.
        """
        result = await self.session.execute(
            select(Subscription).where(Subscription.stripe_customer_id == customer_id)
        )
        return result.scalars().first()

    async def create(
        self,
        workspace_id: uuid.UUID,
        stripe_customer_id: str,
    ) -> Subscription:
        """Persist a new subscription record after Stripe customer creation.

        Args:
            workspace_id: The workspace this subscription belongs to.
            stripe_customer_id: The Stripe customer ID.

        Returns:
            The newly created Subscription.
        """
        sub = Subscription(
            workspace_id=workspace_id,
            stripe_customer_id=stripe_customer_id,
        )
        self.session.add(sub)
        await self.session.commit()
        await self.session.refresh(sub)
        return sub

    async def update(
        self,
        sub: Subscription,
        *,
        stripe_subscription_id: str | None = None,
        stripe_price_id: str | None = None,
        status: SubscriptionStatus | None = None,
        current_period_end: datetime | None = None,
        cancel_at_period_end: bool | None = None,
    ) -> Subscription:
        """Partially update a subscription's Stripe-synced fields.

        Args:
            sub: The Subscription instance to update.
            stripe_subscription_id: Stripe subscription ID if changed.
            stripe_price_id: Stripe price ID if changed.
            status: New subscription status if changed.
            current_period_end: End of the current billing period if changed.
            cancel_at_period_end: Cancellation flag if changed.

        Returns:
            The updated Subscription.
        """
        if stripe_subscription_id is not None:
            sub.stripe_subscription_id = stripe_subscription_id
        if stripe_price_id is not None:
            sub.stripe_price_id = stripe_price_id
        if status is not None:
            sub.status = status
        if current_period_end is not None:
            sub.current_period_end = current_period_end
        if cancel_at_period_end is not None:
            sub.cancel_at_period_end = cancel_at_period_end

        await self.session.commit()
        await self.session.refresh(sub)
        return sub

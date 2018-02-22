import graphene
from django.contrib.auth.models import User
from graphene import AbstractType, ObjectType
from graphene_django import DjangoObjectType

from fishtracker.models import FishCatch, FriendsFishCatches, Lake

from .utils import requires_permission


class UserField(DjangoObjectType):

    class Meta:
        model = User
        only_fields = ('id', 'username', 'email', '')


class FishCatchField(DjangoObjectType):
    shared_with = graphene.List(UserField)

    class Meta:
        model = FishCatch
        exclude_fields = ('friends_fish_catches')

    def resolve_shared_with(self, info):
        return [ffc.user for ffc in self.friends_fish_catches.all()]


class LakeField(DjangoObjectType):

    class Meta:
        model = Lake


class FriendsFishCatchesField(DjangoObjectType):

    class Meta:
        model = FriendsFishCatches


class FishCatchMutation(graphene.Mutation):

    class Arguments:
        description = graphene.String(required=True)
        latitude = graphene.Float(required=True)
        longitude = graphene.Float(required=True)
        lake_id = graphene.String(required=True)

    fish_catch = graphene.Field(FishCatchField)

    def mutate(cls, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Unauthorized")
        fish_catch = FishCatch(**kwargs)
        fish_catch.user = user
        fish_catch.save()
        return FishCatchMutation(fish_catch=fish_catch)


class LakeMutation(graphene.Mutation):
    
    class Arguments:
        name = graphene.String(required=True)

    lake = graphene.Field(LakeField)

    @requires_permission('create_lake')
    def mutate(self, info, **kwargs):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Unauthorized")
        lake = Lake(**kwargs)
        lake.user = user
        lake.save()
        return LakeMutation(lake=Lake.objects.get(pk=lake.id))


class AddFriendFishCatchMutation(graphene.Mutation):

    class Arguments:
        fish_catch_id = graphene.String(required=True)
        friend_id = graphene.Int(required=True)

    shared_fish_catches = graphene.List(FishCatchField)

    def mutate(self, info, fish_catch_id, friend_id):
        user = info.context.user
        fish_catch = FishCatch.objects.get(id=fish_catch_id)
        if fish_catch.user_id != user.id:
            raise Exception("No permission")
        ffc = FriendsFishCatches(
            user_id=friend_id, fish_catch_id=fish_catch_id
        )
        ffc.save()
        my_fish_catches = FishCatch.objects.filter(user_id=user.id)
        return AddFriendFishCatchMutation(
            shared_fish_catches=FishCatch.objects.filter(
                friendsfishcatches__fish_catch__in=my_fish_catches).select_related('user').select_related('lake').distinct()
        )


class Query(graphene.ObjectType):
    lakes = graphene.List(LakeField)
    fish_catches = graphene.List(FishCatchField)
    friends_fish_catch = graphene.List(FishCatchField)
    lake = graphene.Field(LakeField, id=graphene.Int())

    @requires_permission('change_lake')
    def resolve_lake(self, info, id):
        user = info.context.user
        return Lake.objects.get(id=id, user=user)

    def resolve_lakes(self, info, **args):
        user = info.context.user
        return Lake.objects.select_related('user').filter(user_id=user.id).prefetch_related('fish_catches__friends_fish_catches__user')

    def resolve_fish_catches(self, info, **args):
        user = info.context.user
        return FishCatch.objects.select_related('lake').select_related('user').filter(user_id=user.id).prefetch_related('friends_fish_catches__user')

    def resolve_friends_fish_catch(self, info, **args):
        user = info.context.user
        return FishCatch.objects.filter(friends_fish_catches__user_id=user.id).select_related('user').prefetch_related('friends_fish_catches__user').select_related('lake').distinct()


class Mutation(graphene.ObjectType):
    create_fish_catch = FishCatchMutation.Field()
    share_fish_catch = AddFriendFishCatchMutation.Field()
    create_lake = LakeMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)

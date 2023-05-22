# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/classes/50_DomoPage.ipynb.

# %% auto 0
__all__ = ['DomoPage', 'PageLayoutTemplate', 'PageLayoutBackground', 'PageLayoutContent', 'PageLayoutStandard',
           'PageLayoutCompact', 'PageLayout', 'DomoPages']

# %% ../../nbs/classes/50_DomoPage.ipynb 2
from fastcore.basics import patch_to
from dataclasses import dataclass, field

import asyncio
import httpx

import domolibrary.client.DomoAuth as dmda
import domolibrary.classes.DomoUser as dmdu
import domolibrary.utils.DictDot as util_dd

import domolibrary.routes.page as page_routes

# %% ../../nbs/classes/50_DomoPage.ipynb 4
@dataclass
class DomoPage:
    id: str
    title: str = None
    parent_page_id: str = None
    top_page_id: str = None
    auth: dmda.DomoAuth = field(default=None, repr=False)
    owners: list = field(default_factory=list)
    cards: list = field(default_factory=list)
    collections: list = field(default_factory=list)
    children: list = field(default_factory=list)
    is_locked: bool = None

    def display_url(self):
        return f"https://{self.auth.domo_instance}.domo.com/page/{self.id}"

    async def _get_domo_users(self, user_id_ls: [str]):
        import domolibrary.classes.DomoUser as dmu

        return await dmu.DomoUsers.by_id(
            user_ids=user_id_ls, only_allow_one=False, auth=self.auth
        )

    async def _get_domo_groups(self, group_id_ls: [str]):
        import domolibrary.classes.DomoGroup as dmg

        return await asyncio.gather(
            *[
                dmg.DomoGroup.get_by_id(group_id=group_id, auth=self.auth)
                for group_id in group_id_ls
            ]
        )

    async def _get_domo_owners_from_dd(self, owners: util_dd.DictDot):
        tasks = list()
        owner_group_ls = [owner.id for owner in owners if owner.type == "GROUP"]

        if owner_group_ls:
            tasks.append(self._get_domo_groups(owner_group_ls))

        owner_user_ls = [owner.id for owner in owners if owner.type == "USER"]

        if owner_user_ls:
            tasks.append(self._get_domo_users(owner_user_ls))

        res = await asyncio.gather(*tasks)

        print(res)

        return res

# %% ../../nbs/classes/50_DomoPage.ipynb 5
@dataclass
class PageLayoutTemplate:
    content_key: int
    x: int
    y: int
    width: int
    height: int
    type: str
    virtual: bool
    virtual_appendix: bool

    @classmethod
    def _from_json(cls, dd):
        return cls(
            content_key=dd.contentKey,
            x=dd.x,
            y=dd.y,
            width=dd.width,
            height=dd.height,
            type=dd.type,
            virtual=dd.virtual,
            virtual_appendix=dd.virtualAppendix,
        )

    def get_body(self):
        return {
            "contentKey": self.content_key,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "type": self.type,
            "virtual": self.virtual,
            "virtualAppendix": self.virtual_appendix,
        }


@dataclass
class PageLayoutBackground:
    id: int
    crop_height: int
    crop_width: int
    x: int
    y: str
    data_file_id: int
    image_brightness: int
    image_height: int
    image_width: int
    selected_color: str
    text_color: str
    type: str
    is_darkMode: bool
    alpha: float
    src: str

    @classmethod
    def _from_json(cls, dd):
        if dd is not None:
            return cls(
                id=dd.id,
                crop_height=dd.cropHeight,
                crop_width=dd.cropWidth,
                x=dd.x,
                y=dd.y,
                data_file_id=dd.dataFileId,
                image_brightness=dd.imageBrightness,
                image_height=dd.imageHeight,
                image_width=dd.imageWidth,
                selected_color=dd.selectedColor,
                text_color=dd.textColor,
                type=dd.type,
                is_darkMode=dd.darkMode,
                alpha=dd.alpha,
                src=dd.src,
            )
        else:
            return None

    def get_body(self):
        return {
            "id": self.id,
            "cropHeight": self.crop_height,
            "cropWidth": self.crop_width,
            "x": self.x,
            "y": self.y,
            "dataFileId": self.data_file_id,
            "imageBrightness": self.image_brightness,
            "imageHeight": self.image_height,
            "imageWidth": self.image_width,
            "selectedColor": self.selected_color,
            "textColor": self.text_color,
            "type": self.type,
            "darkMode": self.is_darkMode,
            "alpha": self.alpha,
            "src": self.src,
        }


@dataclass
class PageLayoutContent:
    accept_date_filter: bool
    accept_filters: bool
    accept_segments: bool
    card_id: int
    card_urn: str
    compact_interaction_default: bool
    content_key: int
    fit_to_frame: bool
    has_summary: bool
    hide_border: bool
    hide_description: bool
    hide_footer: bool
    hide_margins: bool
    hide_summary: bool
    hide_timeframe: bool
    hide_title: bool
    hide_wrench: bool
    id: int
    summary_number_only: bool
    type: str
    text: str
    background_id: int
    background: PageLayoutBackground

    @classmethod
    def _from_json(cls, dd):
        return cls(
            accept_date_filter=dd.acceptDateFilter,
            accept_filters=dd.acceptFilters,
            accept_segments=dd.acceptSegments,
            card_id=dd.cardId,
            card_urn=dd.cardUrn,
            compact_interaction_default=dd.compactInteractionDefault,
            content_key=dd.contentKey,
            fit_to_frame=dd.fitToFrame,
            has_summary=dd.hasSummary,
            hide_border=dd.hideBorder,
            hide_description=dd.hideDescription,
            hide_footer=dd.hideFooter,
            hide_margins=dd.hideMargins,
            hide_summary=dd.hideSummary,
            hide_timeframe=dd.hideTimeframe,
            hide_title=dd.hideTitle,
            hide_wrench=dd.hideWrench,
            id=dd.id,
            summary_number_only=dd.summaryNumberOnly,
            type=dd.type,
            text=dd.text,
            background_id=dd.backgroundId,
            background=PageLayoutBackground._from_json(dd=dd.background),
        )

    def get_body(self):
        body = {
            "acceptDateFilter": self.accept_date_filter,
            "acceptFilters": self.accept_filters,
            "acceptSegments": self.accept_segments,
            "cardId": self.card_id,
            "cardUrn": self.card_urn,
            "compactInteractionDefault": self.compact_interaction_default,
            "contentKey": self.content_key,
            "fitToFrame": self.fit_to_frame,
            "hasSummary": self.has_summary,
            "hideBorder": self.hide_border,
            "hideDescription": self.hide_description,
            "hideFooter": self.hide_footer,
            "hideMargins": self.hide_margins,
            "hideSummary": self.hide_summary,
            "hideTimeframe": self.hide_timeframe,
            "hideTitle": self.hide_title,
            "hideWrench": self.hide_wrench,
            "id": self.id,
            "summaryNumberOnly": self.summary_number_only,
            "type": self.type,
            "text": self.text,
            "backgroundId": self.background_id,
        }

        if self.background is not None:
            body["background"] = self.background.get_body()
        return body


@dataclass
class PageLayoutStandard:
    aspect_ratio: float
    width: int
    frame_margin: int
    frame_padding: int
    type: str
    template: list[PageLayoutTemplate]

    @classmethod
    def _from_json(cls, dd):
        obj = cls(
            aspect_ratio=dd.aspectRatio,
            width=dd.width,
            frame_margin=dd.frameMargin,
            frame_padding=dd.framePadding,
            type=dd.type,
            template=[],
        )

        if dd.template is not None:
            for template_item in dd.template:
                dc = PageLayoutTemplate._from_json(dd=template_item)
                if dc not in obj.template:
                    obj.template.append(dc)
        return obj


@dataclass
class PageLayoutCompact:
    aspect_ratio: float
    width: int
    frame_margin: int
    frame_padding: int
    type: str
    template: list[PageLayoutTemplate]

    @classmethod
    def _from_json(cls, dd):
        obj = cls(
            aspect_ratio=dd.aspectRatio,
            width=dd.width,
            frame_margin=dd.frameMargin,
            frame_padding=dd.framePadding,
            type=dd.type,
            template=[],
        )
        if dd.template is not None:
            for template_item in dd.template:
                dc = PageLayoutTemplate._from_json(dd=template_item)
                if dc not in obj.template:
                    obj.template.append(dc)
        return obj


@dataclass
class PageLayout:
    id: str
    page_id: str
    is_print_friendly: bool
    is_enabled: bool
    is_dynamic: bool
    has_page_breaks: bool
    content: list[PageLayoutContent]
    standard: PageLayoutStandard
    compact: PageLayoutCompact
    background: PageLayoutBackground

    @classmethod
    def _from_json(cls, dd):
        obj = cls(
            id=dd.layoutId,
            page_id=dd.pageUrn,
            is_print_friendly=dd.printFriendly,
            is_enabled=dd.enabled,
            is_dynamic=dd.isDynamic,
            content=[],
            has_page_breaks=dd.hasPageBreaks,
            standard=PageLayoutStandard._from_json(dd=dd.standard),
            compact=PageLayoutCompact._from_json(dd=dd.compact),
            background=PageLayoutBackground._from_json(dd=dd.background),
        )
        if dd.content is not None:
            for content_item in dd.content:
                dc = PageLayoutContent._from_json(dd=content_item)
                if dc not in obj.content:
                    obj.content.append(dc)
        return obj

    @classmethod
    def generate_new_background_body(cls):
        background_body = {
            "selectedColor": "#EEE000",
            "textColor": "#4A4A4A",
            "type": "COLOR",
            "darkMode": False,
            "alpha": 1,
        }

        return background_body

    def get_body(self):
        body = {
            "layoutId": self.id,
            "pageUrn": self.page_id,
            "printFriendly": self.is_print_friendly,
            "enabled": self.is_enabled,
            "isDynamic": self.is_dynamic,
            "hasPageBreaks": self.has_page_breaks,
            "standard": {
                "aspectRatio": self.standard.aspect_ratio,
                "width": self.standard.width,
                "frameMargin": self.standard.frame_margin,
                "framePadding": self.standard.frame_padding,
                "type": self.standard.type,
            },
            "compact": {
                "aspectRatio": self.compact.aspect_ratio,
                "width": self.compact.width,
                "frameMargin": self.compact.frame_margin,
                "framePadding": self.compact.frame_padding,
                "type": self.compact.type,
            },
        }
        if self.background is not None:
            body["background"] = self.background.get_body()

        if self.content == [] or self.content is None:
            body["content"] = []
        else:
            temp_list = []
            for content_item in self.content:
                temp_list.append(content_item.get_body())
            body["content"] = temp_list

        if self.standard.template is None or self.standard.template == []:
            body["standard"]["template"] = []
        else:
            temp_list = []
            for template_item in self.standard.template:
                temp_list.append(template_item.get_body())
            body["standard"]["template"] = temp_list

        if self.compact.template is None or self.compact.template == []:
            body["compact"]["template"] = []
        else:
            temp_list = []
            for template_item in self.compact.template:
                temp_list.append(template_item.get_body())
            body["compact"]["template"] = temp_list
        return body

# %% ../../nbs/classes/50_DomoPage.ipynb 6
@dataclass
class DomoPage:
    id: str
    title: str = None
    parent_page_id: str = None
    top_page_id: str = None
    auth: dmda.DomoAuth = field(default=None, repr=False)
    owners: list = field(default_factory=list)
    cards: list = field(default_factory=list)
    collections: list = field(default_factory=list)
    children: list = field(default_factory=list)
    is_locked: bool = None
    layout: PageLayout = None

    def display_url(self):
        return f"https://{self.auth.domo_instance}.domo.com/page/{self.id}"

    async def _get_domo_users(self, user_id_ls: [str]):
        import domolibrary.classes.DomoUser as dmu

        return await dmu.DomoUsers.by_id(
            user_ids=user_id_ls, only_allow_one=False, auth=self.auth
        )

    async def _get_domo_groups(self, group_id_ls: [str]):
        import domolibrary.classes.DomoGroup as dmg

        return await asyncio.gather(
            *[
                dmg.DomoGroup.get_by_id(group_id=group_id, auth=self.auth)
                for group_id in group_id_ls
            ]
        )

    async def _get_domo_owners_from_dd(self, owners: util_dd.DictDot):
        tasks = list()
        owner_group_ls = [owner.id for owner in owners if owner.type == "GROUP"]

        if owner_group_ls:
            tasks.append(self._get_domo_groups(owner_group_ls))

        owner_user_ls = [owner.id for owner in owners if owner.type == "USER"]

        if owner_user_ls:
            tasks.append(self._get_domo_users(owner_user_ls))

        res = await asyncio.gather(*tasks)

        return [member for member_ls in res for member in member_ls]

# %% ../../nbs/classes/50_DomoPage.ipynb 7
@patch_to(DomoPage, cls_method=True)
async def _from_bootstrap(cls: DomoPage, page_obj, auth: dmda.DomoAuth = None):
    dd = page_obj
    if isinstance(page_obj, dict):
        dd = util_dd.DictDot(page_obj)

    pg = cls(id=dd.id, title=dd.title, auth=auth)

    if isinstance(dd.owners, list) and len(dd.owners) > 0:
        pg.owners = await pg._get_domo_owners_from_dd(dd.owners)

    if isinstance(dd.children, list) and len(dd.children) > 0:
        pg.children = await asyncio.gather(
            *[
                cls._from_bootstrap(page_obj=child_dd, auth=auth)
                for child_dd in dd.children
                if child_dd.type == "page"
            ]
        )

        [print(other_dd) for other_dd in dd.children if other_dd.type != "page"]

    return pg

# %% ../../nbs/classes/50_DomoPage.ipynb 10
@patch_to(DomoPage, cls_method=True)
async def _from_content_stacks_v3(cls: DomoPage, page_obj, auth: dmda.DomoAuth = None):
    # import domolibrary.classes.DomoCard as dc

    dd = page_obj
    if isinstance(page_obj, dict):
        dd = util_dd.DictDot(page_obj)

    pg = cls(
        id=dd.id,
        title=dd.title,
        parent_page_id=dd.page.parentPageId,
        collections=dd.collections,
        auth=auth,
    )

    if hasattr(dd, "pageLayoutV4") and dd.pageLayoutV4 is not None:
        dd_layout = dd.pageLayoutV4
        pg.layout = PageLayout._from_json(dd=dd.pageLayoutV4)

    if dd.page.owners and len(dd.page.owners) > 0:
        pg.owners = await pg._get_domo_owners_from_dd(dd.page.owners)

    # if dd.cards and len(dd.cards) > 0:
    #     pg.cards = await asyncio.gather(
    #         *[dc.DomoCard.get_from_id(id=card.id, auth=auth) for card in dd.cards])

    return pg


@patch_to(DomoPage, cls_method=True)
async def get_by_id(
    cls: DomoPage,
    page_id: str,
    auth: dmda.DomoAuth,
    return_raw: bool = False,
    debug_api: bool = False,
    include_layout: bool = False,
):
    res = await page_routes.get_page_by_id(
        auth=auth, page_id=page_id, debug_api=debug_api, include_layout=include_layout
    )

    if return_raw:
        return res

    if not res.status == 200:
        return

    pg = await cls._from_content_stacks_v3(page_obj=res.response, auth=auth)

    return pg

# %% ../../nbs/classes/50_DomoPage.ipynb 13
@patch_to(DomoPage, cls_method=True)
async def _from_adminsummary(cls, page_obj, auth: dmda.DomoAuth):
    import domolibrary.classes.DomoCard as dmc

    dd = page_obj
    if isinstance(page_obj, dict):
        dd = util_dd.DictDot(page_obj)

    pg = cls(
        id=dd.id or dd.pageId,
        title=dd.title or dd.pageTitle,
        parent_page_id=dd.parentPageId,
        top_page_id=dd.topPageId,
        collections=dd.collections,
        is_locked=dd.locked,
        auth=auth,
    )

    if dd.page and dd.page.owners and len(dd.page.owners) > 0:
        pg.owners = await pg._get_domo_owners_from_dd(dd.page.owners)

    if dd.cards and len(dd.cards) > 0:
        pg.cards = await asyncio.gather(
            *[dmc.DomoCard.get_from_id(id=card.id, auth=auth) for card in dd.cards]
        )

    return pg

# %% ../../nbs/classes/50_DomoPage.ipynb 14
@patch_to(DomoPage)
async def get_accesslist(
    self,
    auth: dmda.DomoAuth = None,
    is_expand_users: bool = False,
    return_raw: bool = False,
    debug_api: bool = False,
):
    auth = auth or self.auth

    res = await page_routes.get_page_access_list(
        auth=auth, is_expand_users=is_expand_users, page_id=self.id, debug_api=debug_api
    )

    if return_raw:
        return res

    if not res.is_success:
        raise Exception("error getting access list")

    import domolibrary.classes.DomoUser as dmu
    import domolibrary.classes.DomoGroup as dmg

    tasks = await asyncio.gather(
        dmu.DomoUsers.by_id(
            user_ids=[user.get("id") for user in res.response.get("users")],
            only_allow_one=False,
            auth=auth,
        ),
        *[
            dmg.DomoGroup.get_by_id(group_id=group.get("id"), auth=auth)
            for group in res.response.get("groups")
        ]
    )

    res.response.update({"users": tasks[0], "groups": tasks[1:]})

    return res.response

# %% ../../nbs/classes/50_DomoPage.ipynb 17
@patch_to(DomoPage)
async def share(self: DomoPage,
                     auth: dmda.DomoAuth,
                     domo_users: list = None,  # DomoUsers to share page with,
                     domo_groups: list = None,  # DomoGroups to share page with
                     message: str = None,  # message for automated email
                     debug_api: bool = False, session: httpx.AsyncClient = None):

    import domolibrary.routes.datacenter as datacenter_routes

    if domo_groups : domo_groups = domo_groups if isinstance(domo_groups, list) else [domo_groups]
    if domo_users : domo_users = domo_users if isinstance(domo_users, list) else [domo_users]


    res = await datacenter_routes.share_resource(
        auth=auth,
        resource_ids=[self.id],
        resource_type=datacenter_routes.ShareResource_Enum.PAGE,
        group_ids=[group.id for group in domo_groups] if domo_groups else None,
        user_ids=[user.id for user in domo_users] if domo_users else None,
        message=message,
        debug_api=debug_api, session=session,
    )

    return res


# %% ../../nbs/classes/50_DomoPage.ipynb 20
@dataclass
class DomoPages:
    pass

# %% ../../nbs/classes/50_DomoPage.ipynb 21
@patch_to(DomoPages, cls_method=True)
async def get_pages(
    cls: DomoPages,
    auth=dmda.DomoAuth,
    return_raw: bool = False,
    debug_loop: bool = False,
    debug_api: bool = False,
    session: httpx.AsyncClient = None,
):
    is_close_session = False if session else True

    session = session or httpx.AsyncClient()

    try:
        res = await page_routes.get_pages_adminsummary(
            auth=auth, debug_loop=False, debug_api=False, session=session
        )

        if return_raw:
            return res

        if not res.is_success:
            raise Exception("unable to retrieve pages")

        return await asyncio.gather(
            *[
                DomoPage._from_adminsummary(page_obj, auth=auth)
                for page_obj in res.response
            ]
        )

    finally:
        if is_close_session:
            await session.aclose()

# %% ../../nbs/classes/50_DomoPage.ipynb 24
from datetime import datetime
from utils import convert


@patch_to(DomoPage, cls_method=True)
async def update_layout(
    cls, auth: dmda.DomoAuth, body: dict, layout_id: str, debug_api: bool = False
):
    datetime_now = datetime.now()
    start_time_epoch = convert.convert_datetime_to_epoch_millisecond(datetime_now)

    res_writelock = await page_routes.put_writelock(
        auth=auth,
        layout_id=layout_id,
        user_id=auth.user_id,
        epoch_time=start_time_epoch,
    )
    if res_writelock.status == 200:
        res = await page_routes.update_page_layout(
            auth=auth, body=body, layout_id=layout_id, debug_api=debug_api
        )

        if res.status != 200:
            return False

        res_writelock = await page_routes.delete_writelock(
            auth=auth, layout_id=layout_id
        )
        if res_writelock.status != 200:
            return False

    else:
        return False

    return True

import asyncio
import aiohttp
from dataclasses import dataclass, field

from .routes import page_routes
from .DomoAuth import DomoDeveloperAuth, DomoFullAuth
from ..utils.DictDot import DictDot
from ..utils.Base import Base
from ..utils import convert
from typing import Any, List
from pprint import pprint
from datetime import datetime



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
            type= dd.type,
            virtual=dd.virtual,
            virtual_appendix = dd.virtualAppendix,
           
        )
    
    def get_body(self):
        return {
            "contentKey": self.content_key,
            "x": self.x,
            "y":self.y,
            "width": self.width,
            "height": self.height,
            "type":self.type,
            "virtual":self.virtual,
            "virtualAppendix":self.virtual_appendix
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
            x = dd.x,
            y = dd.y,
            data_file_id = dd.dataFileId,
            image_brightness = dd.imageBrightness,
            image_height = dd.imageHeight,
            image_width = dd.imageWidth,
            selected_color = dd.selectedColor,
            text_color = dd.textColor,
            type = dd.type,
            is_darkMode = dd.darkMode,
            alpha = dd.alpha,
            src = dd.src
            
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
            "src": self.src
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
    hide_margins:bool
    hide_summary: bool
    hide_timeframe: bool
    hide_title: bool
    hide_wrench: bool
    id: int
    summary_number_only:bool
    type: str
    text: str
    background_id : int
    background : PageLayoutBackground
    
    
    
    @classmethod
    def _from_json(cls, dd):
        return cls(
            accept_date_filter=dd.acceptDateFilter,
            accept_filters=dd.acceptFilters,
            accept_segments=dd.acceptSegments,
            card_id=dd.cardId,
            card_urn=dd.cardUrn,
            compact_interaction_default= dd.compactInteractionDefault,
            content_key=dd.contentKey,
            fit_to_frame = dd.fitToFrame,
            has_summary=dd.hasSummary,
            hide_border = dd.hideBorder,
            hide_description= dd.hideDescription,
            hide_footer = dd.hideFooter,
            hide_margins = dd.hideMargins,
            hide_summary = dd.hideSummary,
            hide_timeframe = dd.hideTimeframe,
            hide_title = dd.hideTitle,
            hide_wrench = dd.hideWrench,
            id = dd.id,
            summary_number_only=dd.summaryNumberOnly,
            type = dd.type,
            text = dd.text,
            background_id = dd.backgroundId,
            background = PageLayoutBackground._from_json(
                    dd=dd.background)
            
        )
    
    def get_body(self):
        body = {
            "acceptDateFilter": self.accept_date_filter,
            "acceptFilters": self.accept_filters,
            "acceptSegments":self.accept_segments,
            "cardId": self.card_id,
            "cardUrn": self.card_urn,
            "compactInteractionDefault":self.compact_interaction_default,
            "contentKey":self.content_key,
            "fitToFrame":self.fit_to_frame,
            "hasSummary":self.has_summary,
            "hideBorder":self.hide_border,
            "hideDescription":self.hide_description,
            "hideFooter":self.hide_footer,
            "hideMargins":self.hide_margins,
            "hideSummary":self.hide_summary,
            "hideTimeframe":self.hide_timeframe,
            "hideTitle":self.hide_title,
            "hideWrench":self.hide_wrench,
            "id":self.id,
            "summaryNumberOnly":self.summary_number_only,
            "type":self.type,
            "text":self.text,
            "backgroundId":self.background_id
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
            type = dd.type, 
            template = []
        )
            
        if dd.template is not None:
            for template_item in dd.template:
                dc = PageLayoutTemplate._from_json(
                    dd=template_item)
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
            type = dd.type,
            template = []
        )
        if dd.template is not None:
            for template_item in dd.template:
                dc = PageLayoutTemplate._from_json(
                    dd=template_item)
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
    has_page_breaks : bool
    content : list[PageLayoutContent]
    standard : PageLayoutStandard
    compact : PageLayoutCompact
    background: PageLayoutBackground
    
    @classmethod
    def _from_json(cls, dd):
    
        obj= cls(
            id=dd.layoutId,
            page_id=dd.pageUrn,
            is_print_friendly=dd.printFriendly,
            is_enabled=dd.enabled,
            is_dynamic=dd.isDynamic,
            content = [],
            has_page_breaks = dd.hasPageBreaks,
            standard = PageLayoutStandard._from_json(
                    dd=dd.standard),
            compact = PageLayoutCompact._from_json(
                    dd=dd.compact),
            background =PageLayoutBackground._from_json(
                    dd=dd.background)
        )
        if dd.content is not None:
            for content_item in dd.content:
                dc = PageLayoutContent._from_json(
                    dd=content_item)
                if dc not in obj.content:
                    obj.content.append(dc)
        return obj
        
    
    @classmethod
    def generate_new_background_body (cls):
        background_body= {
         
            "selectedColor": "#EEE000",
            "textColor": "#4A4A4A",
            "type": "COLOR",
            "darkMode": False,
            "alpha": 1
        }
        
        return background_body

    
    def get_body (self):
        body = {
        "layoutId": self.id,
        "pageUrn": self.page_id,
        "printFriendly" : self.is_print_friendly,
        "enabled": self.is_enabled,
        "isDynamic": self.is_dynamic,
        "hasPageBreaks": self.has_page_breaks,
        "standard" : {
            "aspectRatio":self.standard.aspect_ratio,
            "width": self.standard.width,
            "frameMargin": self.standard.frame_margin,
            "framePadding": self.standard.frame_padding,
            "type": self.standard.type
            },
        "compact" : {
            "aspectRatio":self.compact.aspect_ratio,
            "width": self.compact.width,
            "frameMargin": self.compact.frame_margin,
            "framePadding": self.compact.frame_padding,
            "type": self.compact.type
            }
         }
        if self.background is not None:
            body["background"] = self.background.get_body()

        if  self.content ==[] or self.content is None:
            body["content"] = []
        else:
            temp_list = []
            for content_item in self.content:
                temp_list.append(content_item.get_body())
            body["content"]= temp_list
            
            
        if self.standard.template is None or self.standard.template==[]:
            body["standard"]["template"]=[]
        else:
            temp_list = []
            for template_item in self.standard.template:
                temp_list.append(template_item.get_body())
            body["standard"]["template"]= temp_list
            
        if self.compact.template is None or self.compact.template==[]:
            body["compact"]["template"]=[]
        else:
            temp_list = []
            for template_item in self.compact.template:
                temp_list.append(template_item.get_body())
            body["compact"]["template"]= temp_list
        return body

@dataclass
class DomoPage(Base):
    id: str
    title: str = None
    parent_page_id: str = None
    domo_instance: str = None
    full_auth: DomoFullAuth = None
    owners: list = field(default_factory=list)
    cards: list = field(default_factory=list)
    collections: list = field(default_factory=list)
    layout: PageLayout = None
    
    def __post_init__(self, full_auth=None):
        Base().__init__()

        if full_auth:
            self.domo_instance = full_auth.domo_instance
            self.full_auth = full_auth
        # self.Definition = CardDefinition(self)

    def display_url(self):
        return f'https://{self.domo_instance}.domo.com/page/{self.id}'

    @classmethod
    async def get_from_id(cls, page_id: str, full_auth: DomoFullAuth, debug: bool = False, include_layout: bool = False):
        import Library.DomoClasses.DomoCard as dc
        res = await page_routes.get_page_by_id(full_auth=full_auth, page_id=page_id, debug=debug, include_layout=include_layout)

        if res.status == 200:
            dd = DictDot(res.response)
            pg = cls(
                id=dd.id,
                domo_instance=full_auth.domo_instance,
                title=dd.title,
                parent_page_id=dd.page.parentPageId,
                owners=dd.page.owners,
                collections=dd.collections
            )
            if hasattr(dd, 'pageLayoutV4'):
                dd_layout = dd.pageLayoutV4
                pg.layout =PageLayout._from_json(
                    dd=dd.pageLayoutV4)

            pg.cards = await asyncio.gather(
                *[dc.DomoCard.get_from_id(id=card.id, full_auth=full_auth) for card in dd.cards])

            return pg

    @classmethod
    async def get_cards(cls, full_auth, page_id, debug: bool = False, session: aiohttp.ClientSession = None):
        try:
            import Library.DomoClasses.DomoCard as dc
            close_session = False if session else True

            if not session:
                session = aiohttp.ClientSession()

            res = await page_routes.get_page_definition(full_auth=full_auth, page_id=page_id, debug=debug, session=session)

            if res.status == 200:
                json = res.response

                card_list = [dc.DomoCard(id=card.get(
                    'id'), full_auth=full_auth) for card in json.get('cards')]

                return card_list

            else:
                return None

        finally:
            if close_session:
                await session.close()

    async def get_datasets(full_auth, page_id, debug: bool = False, session: aiohttp.ClientSession = None):
        try:
            import Library.DomoClasses.DomoDataset as dmds
            close_session = False if session else True

            if not session:
                session = aiohttp.ClientSession()

            res = await page_routes.get_page_definition(full_auth=full_auth, page_id=page_id, debug=debug, session=session)

            if res.status == 200:
                json = res.response

                dataset_ls = [card.get('datasources')
                              for card in json.get('cards')]

                return [dmds.DomoDataset(id=ds.get('dataSourceId'), full_auth=full_auth) for ds_ls in dataset_ls for ds in ds_ls]

            else:
                return None

        finally:
            if close_session:
                await session.close()

    @classmethod
    async def update_layout(cls,
                         full_auth: DomoFullAuth,
                         body: dict,
                         layout_id: str,
                         debug: bool = False,
                         log_results: bool = False,
                        session: aiohttp.ClientSession = None):
        datetime_now = datetime.now()
        start_time_epoch = convert.convert_datetime_to_epoch_millisecond(
            datetime_now)
        
        res_writelock = await page_routes.put_writelock(full_auth=full_auth, 
                                                        layout_id = layout_id,
                                                        user_id=full_auth.user_id,
                                                         epoch_time = start_time_epoch)
        if res_writelock.status == 200:
        
            res = await page_routes.update_page_layout(full_auth=full_auth,
                                          body=body,
                                       layout_id = layout_id,
                                       debug=debug,
                                       log_results=log_results)

    
            if res.status != 200:
                return False
            
            res_writelock = await page_routes.delete_writelock(full_auth=full_auth, 
                                                        layout_id = layout_id)
            if res_writelock.status != 200:
                return False
            
        else:
            return False

        return True
    
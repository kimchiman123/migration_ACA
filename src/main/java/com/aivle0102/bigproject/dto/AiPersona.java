package com.aivle0102.bigproject.dto;

import lombok.Getter;
import lombok.Setter;

import java.util.List;

@Getter
@Setter
public class AiPersona {

    private String country;
    private String ageGroup; //ex."21-30"
    private String personaName;

    private String lifestyle; //?쇱씠?꾩뒪???
    private String foodPreference; //?좏샇?뚯떇

    private List<String> purchaseCriteria; //援щℓ湲곗?(援щℓ寃곗젙 ??蹂대뒗 ??ぉ?? ex.媛寃? ?곸뼇?깅텇 ??
    private String attitudeToKFood; //K-food ??????쇰쭏??愿?ъ엳?붿?, 醫뗭븘?섎뒗吏...
    private String evaluationPerspective; //?대떦 ?섎Ⅴ?뚮굹???ъ궗 ?됯? 湲곗?
}

package com.aivle0102.bigproject.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class PersonaEvaluation {

    private String country;
    private String ageGroup;
    private String personaName;

    private int totalScore; //醫낇빀 ?먯닔 0~100
    private int tasteScore; //留??됯? 0~100
    private int priceScore;  //媛寃??됯? 0~100
    private int healthScore; //?곸뼇/嫄닿컯 ?됯? 0~100

    private String positiveFeedback; //?μ젏 ?쇰뱶諛?
    private String negativeFeedback; //?⑥젏 ?쇰뱶諛?

    private String purchaseIntent; //援щℓ?щ? (YES / NO / MAYBE)
}

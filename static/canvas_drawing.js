var CARD_W2H_RATIO = 5.0 / 7.0;
var SUIT_W2H_RATIO = 3.0 / 4.0;
var CARD_HEIGHT = 100;

var card_back_img = new Image();   // Create new img element
card_back_img.src = "http://cdn.shopify.com/s/files/1/0200/7616/products/playing-cards-bicycle-rider-back-2_grande.png?v=1494193481";

function render_state(player_id, state) {
    var c = document.getElementById("tableCanvas");
    var ctx = c.getContext("2d");
    ctx.clearRect(0, 0, c.width, c.height);
    ctx.fillStyle = "#277714";
    ctx.fillRect(0, 0, c.width, c.height);

    var font_size = 50;
    ctx.fillStyle = "#00ff00";
    ctx.font = font_size + 'px Arial';

    other_player_id = null;
    for (pid in state['players']) {
        if (player_id != pid) {
            other_player_id = pid;
        }
    }

    ctx.fillText("YOU", 225, 300 + font_size);
    // ctx.fillText("POT", 400, 200 + font_size);
    
    if (state['players'][player_id] > 0) {
        render_card_back(ctx, 200, 200);
    }
    if (state['players'][other_player_id] > 0) {
        render_card_back(ctx, 200, 50);
    }
    
    ctx.fillText(state['players'][player_id], 200, 200 + font_size);
    ctx.fillText(state['players'][other_player_id], 200, 50 + font_size);

    if (state['pot'].length > 0) {
        render_card_back(ctx, 400, 125);
    }
    ctx.fillText(state['pot'].length, 400, 125 + font_size);

    if (state['drawn_cards'][player_id] != null) {
        render_card(ctx, 300, 200, state['drawn_cards'][player_id]);
    }
    if (state['drawn_cards'][other_player_id] != null) {
        render_card(ctx, 300, 50, state['drawn_cards'][other_player_id]);
    }
}


function render_card_back(ctx, x, y) {
    ctx.drawImage(card_back_img, x, y, CARD_HEIGHT * CARD_W2H_RATIO, CARD_HEIGHT);
}

function render_card(ctx, x, y, card) {
    var font_size = 30;
    ctx.font = font_size + 'px Arial';

    var suit = card.split(" ")[0];
    var rank = card.split(" ")[1];

    ctx.fillStyle = "white";
    roundRect(ctx, x, y, CARD_HEIGHT * CARD_W2H_RATIO, CARD_HEIGHT, undefined, true);

    if (suit == 'H' || suit == 'D') {
        ctx.fillStyle = 'red';
    } else {
        ctx.fillStyle = 'black';
    }

    ctx.fillText(rank, x + 10, y + 10 + font_size);
    if (suit == 'H') {
        drawHeart(ctx, x + 20, y + 20 + font_size, font_size * SUIT_W2H_RATIO, font_size);
    } else if (suit == 'D') {
        drawDiamond(ctx, x + 20, y + 20 + font_size, font_size * SUIT_W2H_RATIO, font_size);
    } else if (suit == 'S') {
        drawSpade(ctx, x + 20, y + 20 + font_size, font_size * SUIT_W2H_RATIO, font_size);
    } else if (suit == 'C') {
        drawClub(ctx, x + 20, y + 20 + font_size, font_size * SUIT_W2H_RATIO, font_size);
    }

    ctx.fillStyle = 'black';
}

/**
 * Draws a rounded rectangle using the current state of the canvas.
 * If you omit the last three params, it will draw a rectangle
 * outline with a 5 pixel border radius
 * @param {CanvasRenderingContext2D} ctx
 * @param {Number} x The top left x coordinate
 * @param {Number} y The top left y coordinate
 * @param {Number} width The width of the rectangle
 * @param {Number} height The height of the rectangle
 * @param {Number} [radius = 5] The corner radius; It can also be an object 
 *                 to specify different radii for corners
 * @param {Number} [radius.tl = 0] Top left
 * @param {Number} [radius.tr = 0] Top right
 * @param {Number} [radius.br = 0] Bottom right
 * @param {Number} [radius.bl = 0] Bottom left
 * @param {Boolean} [fill = false] Whether to fill the rectangle.
 * @param {Boolean} [stroke = true] Whether to stroke the rectangle.
 */
function roundRect(ctx, x, y, width, height, radius, fill, stroke) {
    if (typeof stroke == 'undefined') {
        stroke = true;
    }
    if (typeof radius === 'undefined') {
        radius = 5;
    }
    if (typeof radius === 'number') {
        radius = {tl: radius, tr: radius, br: radius, bl: radius};
    } else {
        var defaultRadius = {tl: 0, tr: 0, br: 0, bl: 0};
        for (var side in defaultRadius) {
            radius[side] = radius[side] || defaultRadius[side];
        }
    }
    ctx.beginPath();
    ctx.moveTo(x + radius.tl, y);
    ctx.lineTo(x + width - radius.tr, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius.tr);
    ctx.lineTo(x + width, y + height - radius.br);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius.br, y + height);
    ctx.lineTo(x + radius.bl, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius.bl);
    ctx.lineTo(x, y + radius.tl);
    ctx.quadraticCurveTo(x, y, x + radius.tl, y);
    ctx.closePath();
    if (fill) {
        ctx.fill();
    }
    if (stroke) {
        ctx.stroke();
    }
}

// Thanks to this website for drawing suits.
// http://www.java2s.com/Tutorials/Javascript/Canvas_How_to/Shape/Draw_Spade_Heart_Club_Diamond.htm
function drawSpade(context, x, y, width, height) {
    context.save();
    var bottomWidth = width * 0.7;
    var topHeight = height * 0.7;
    var bottomHeight = height * 0.3;
    
    context.beginPath();
    context.moveTo(x, y);
    
    // top left of spade          
    context.bezierCurveTo(
        x, y + topHeight / 2, // control point 1
        x - width / 2, y + topHeight / 2, // control point 2
        x - width / 2, y + topHeight // end point
    );
    
    // bottom left of spade
    context.bezierCurveTo(
        x - width / 2, y + topHeight * 1.3, // control point 1
        x, y + topHeight * 1.3, // control point 2
        x, y + topHeight // end point
    );
    
    // bottom right of spade
    context.bezierCurveTo(
        x, y + topHeight * 1.3, // control point 1
        x + width / 2, y + topHeight * 1.3, // control point 2
        x + width / 2, y + topHeight // end point
    );
    
    // top right of spade
    context.bezierCurveTo(
        x + width / 2, y + topHeight / 2, // control point 1
        x, y + topHeight / 2, // control point 2
        x, y // end point
    );
    
    context.closePath();
    context.fill();
    
    // bottom of spade
    context.beginPath();
    context.moveTo(x, y + topHeight);
    context.quadraticCurveTo(
        x, y + topHeight + bottomHeight, // control point
        x - bottomWidth / 2, y + topHeight + bottomHeight // end point
    );
    context.lineTo(x + bottomWidth / 2, y + topHeight + bottomHeight);
    context.quadraticCurveTo(
        x, y + topHeight + bottomHeight, // control point
        x, y + topHeight // end point
    );
    context.closePath();
    context.fillStyle = "black";
    context.fill();
    context.restore();
}

function drawHeart(context, x, y, width, height){
    context.save();
    context.beginPath();
    var topCurveHeight = height * 0.3;
    context.moveTo(x, y + topCurveHeight);
    // top left curve
    context.bezierCurveTo(
        x, y, 
        x - width / 2, y, 
        x - width / 2, y + topCurveHeight
    );
            
    // bottom left curve
    context.bezierCurveTo(
        x - width / 2, y + (height + topCurveHeight) / 2, 
        x, y + (height + topCurveHeight) / 2, 
        x, y + height
    );
            
    // bottom right curve
    context.bezierCurveTo(
        x, y + (height + topCurveHeight) / 2, 
        x + width / 2, y + (height + topCurveHeight) / 2, 
        x + width / 2, y + topCurveHeight
    );
            
    // top right curve
    context.bezierCurveTo(
        x + width / 2, y, 
        x, y, 
        x, y + topCurveHeight
    );
            
    context.closePath();
    context.fillStyle = "red";
    context.fill();
    context.restore();
}
        
function drawClub(context, x, y, width, height){
    context.save();
    var circleRadius = width * 0.3;
    var bottomWidth = width * 0.5;
    var bottomHeight = height * 0.35;
    context.fillStyle = "black";
    
    // top circle
    context.beginPath();
    context.arc(
        x, y + circleRadius + (height * 0.05), 
        circleRadius, 0, 2 * Math.PI, false
    );
    context.fill();
            
    // bottom right circle
    context.beginPath();
    context.arc(
        x + circleRadius, y + (height * 0.6), 
        circleRadius, 0, 2 * Math.PI, false
    );
    context.fill();
            
    // bottom left circle
    context.beginPath();
    context.arc(
        x - circleRadius, y + (height * 0.6), 
        circleRadius, 0, 2 * Math.PI, false
    );
    context.fill();
            
    // center filler circle
    context.beginPath();
    context.arc(
        x, y + (height * 0.5), 
        circleRadius / 2, 0, 2 * Math.PI, false
    );
    context.fill();
            
    // bottom of club
    context.moveTo(x, y + (height * 0.6));
    context.quadraticCurveTo(
        x, y + height, 
        x - bottomWidth / 2, y + height
    );
    context.lineTo(x + bottomWidth / 2, y + height);
    context.quadraticCurveTo(
        x, y + height, 
        x, y + (height * 0.6)
    );
    context.closePath();
    context.fill();
    context.restore();
}
        
function drawDiamond(context, x, y, width, height){
    context.save();
    context.beginPath();
    context.moveTo(x, y);
    
    // top left edge
    context.lineTo(x - width / 2, y + height / 2);
    
    // bottom left edge
    context.lineTo(x, y + height);
    
    // bottom right edge
    context.lineTo(x + width / 2, y + height / 2);
    
    // closing the path automatically creates
    // the top right edge
    context.closePath();
    
    context.fillStyle = "red";
    context.fill();
    context.restore();
}